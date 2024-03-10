#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Classes and functions for making releases and publishing them.

import hashlib
import json
import logging
import os
import re
import subprocess

from git import Repo
from github import Github

logger = logging.getLogger(f'poptrackerlib.release')


def create_release(version, note, prerelease=False, repo_dir=None):
    """Create a new release on GitHub.  This should be called from a repository script.

    Args:
        version (str): The version number of the release.
        note (str): The release notes.
        prerelease (bool): Whether the release is a pre-release.
        repo_dir (str): The directory of the repository.  If not provided, current directory is used.

    Returns:
        Release: The new release object.
    """

    if repo_dir is None:
        repo_dir = os.getcwd()

    if not re.match(r'^\d+(\.\d+)+$', version):
        raise ValueError('Invalid version number.')

    tag = title = 'v' + version

    # Make sure we have GitHub OAuth token from command line first.
    process = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, check=True)
    token = process.stdout.strip()

    repo = Repo(repo_dir)

    # Get origin URL and parse out just the owner/name path.
    remote = getattr(repo.remotes, 'origin', None)
    if not remote:
        raise ValueError('No origin remote found.')

    remote_path = repo.remotes.origin.url
    remote_path = remote_path.rsplit(':')[-1]
    remote_path = '/'.join(remote_path.rsplit('/', 2)[1:])
    if remote_path.endswith('.git'):
        remote_path = remote_path[:-4]

    repo_name = remote_path.rsplit('/', 1)[-1]

    # Make sure manifest version matches the release version.  If not, update it and commit to be in the ZIP.
    manifest_file = os.path.join(repo_dir, 'manifest.json')
    with open(manifest_file) as f:
        manifest = json.load(f)

    if manifest['package_version'] != version:
        logger.info(f'Updating manifest.json version to {version}')
        manifest['package_version'] = version

        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=4)
            f.write('\n')  # Trailing newline.

        repo.index.add([manifest_file])
        repo.index.commit(f'{tag} release')
        repo.remotes.origin.push()

    # Build output file.  Include readme and manifest files, and any directories.
    path = []
    for name in os.listdir(repo_dir):
        if name in ('LICENSE', 'README.md', 'manifest.json') or (
                os.path.isdir(os.path.join(repo_dir, name)) and
                not name.startswith('.') and
                not name.startswith('_')
        ):
            path.append(name)

    output_file = os.path.join(repo_dir, repo_name + '.zip')
    logger.info(f'Creating {output_file}')
    with open(output_file, 'wb') as f:
        repo.archive(f, 'main', format='zip', path=path)

    # Get SHA256 hash of ZIP file.
    with open(output_file, 'rb') as f:
        sha256 = hashlib.file_digest(f, 'sha256').hexdigest()

    # Read current versions and create new entry from release notes.
    versions_file = os.path.join(repo_dir, 'versions.json')
    with open(versions_file) as f:
        versions = json.load(f)

    existing = {v['package_version'] for v in versions['versions']}
    if version in existing:
        raise ValueError(f'Version {version} already exists in versions.json')

    new_version = {
        'package_version': version,
        'download_url': '',  # Placeholder for field order.
        'sha256': sha256,
        'changelog': note,
    }

    # Publish a new release to GitHub using OAuth token from command line.
    # Use notes as bullet points in the release body.
    logger.info(f'Publishing release {version}')

    g = Github(token)
    remote_repo = g.get_repo(remote_path)
    binsha = repo.commit('main').binsha
    release = remote_repo.create_git_tag_and_release(tag, tag, title, note, binsha.hex(), 'commit',
                                                     prerelease=prerelease)
    attachment = release.upload_asset(output_file, label=os.path.split(output_file)[1])
    new_version['download_url'] = attachment.browser_download_url

    # Add download URL to new versions entry at the front and commit it to the repository.
    logger.info(f'Updating versions.json')
    versions['versions'].insert(0, new_version)
    with open(versions_file, 'w') as f:
        json.dump(versions, f, indent=4)
        f.write('\n')  # Trailing newline.

    repo.index.add(['versions.json'])
    repo.index.commit(f'{tag} release')
    repo.remotes.origin.push()

    # Done.
    logger.info(f'Release {version} published')
