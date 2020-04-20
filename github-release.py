#! /usr/bin/env python3

"""
This is a quick-and-dirty script to upload release assets to Github via the API.
Currently, we do not use this script and rely instead on the github-release binary. This
is just in case the github-release binary stops working (as it has before).

Run script with:

    GITHUB_TOKEN=s3cr3t ./github-release.py v3.00.00 ./dist/tutor-openedx-3.00.00.tar.gz "tutor-$(uname -s)_$(uname -m)"
"""

import argparse
import os
from urllib.parse import urlencode

import requests

HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "token {}".format(os.environ["GITHUB_TOKEN"]),
}
RELEASES_URL = "https://api.github.com/repos/overhangio/tutor/releases"


def main():
    parser = argparse.ArgumentParser(
        description="Create github releases and upload assets"
    )
    parser.add_argument("tag")
    parser.add_argument("asset")
    parser.add_argument("asset_name")
    args = parser.parse_args()
    release = get_or_create_release(args.tag)
    overwrite_asset(args.asset, args.asset_name, release)


def get_or_create_release(tag):
    # https://developer.github.com/v3/repos/releases/#get-a-release-by-tag-name
    url = "{}/tags/{}".format(RELEASES_URL, tag)
    response = requests.get(url)
    if response.status_code == 200:
        print("Release {} already exists".format(tag))
        return response.json()

    print("Creating release {}".format(tag))
    description = open(
        os.path.join(os.path.dirname("__file__"), "docs", "_release_description.md")
    ).read()
    params = {"tag_name": tag, "name": tag, "body": description}
    # https://developer.github.com/v3/repos/releases/#create-a-release
    return requests.post(RELEASES_URL, json=params, headers=HEADERS,).json()


def overwrite_asset(asset, asset_name, release):
    # https://developer.github.com/v3/repos/releases/#list-assets-for-a-release
    url = "{}/{}/assets".format(RELEASES_URL, release["id"])
    for existing_asset in requests.get(url).json():
        if existing_asset["name"] == asset_name:
            print("Deleting existing asset")
            # https://developer.github.com/v3/repos/releases/#delete-a-release-asset
            delete_url = "{}/assets/{}".format(RELEASES_URL, existing_asset["id"])
            response = requests.delete(delete_url, headers=HEADERS)
            if response.status_code != 204:
                print(response, response.content)
                raise ValueError("Could not delete asset")
    print("Uploading asset")
    upload_asset(asset, asset_name, release)


def upload_asset(asset, asset_name, release):
    upload_url = release["upload_url"].replace(
        "{?name,label}", "?" + urlencode({"name": asset_name})
    )
    files = {"file": (asset_name, open(asset, "rb"))}
    response = requests.post(upload_url, files=files, headers=HEADERS)
    if response.status_code > 299:
        print(response, response.content)
        raise ValueError("Could not upload asset to release")


if __name__ == "__main__":
    main()
