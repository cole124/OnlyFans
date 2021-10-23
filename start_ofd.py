#!/usr/bin/env python3
import sys
import argparse
import traceback
import time
import os
import asyncio
import tests.main_test as main_test
from helpers.CombineDatabases import process_root, CombineFiles, dbFiles

parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('--like_content', dest='like_content', default='', choices=['true', 'false'],
                    help='Like Users content while processing')

parser.add_argument('--models', dest='models', default='')

parser.add_argument('--whitelist', dest='whitelist', default='')

parser.add_argument('--blacklist', dest='blacklist', default='')

args = parser.parse_args()

try:

    main_test.version_check()
    main_test.check_config()
    main_test.check_profiles()

    if __name__ == "__main__":
        import datascraper.main_datascraper as main_datascraper
        import helpers.main_helper as main_helper

        config_path = os.path.join(".settings", "config.json")
        json_config, json_config2 = main_helper.get_config(config_path)

        json_settings = main_helper.process_settings(
            json_config["settings"], args)
        # print(args.like_content)
        print("-------------------------------------------------------------------")
        print("Settings:")
        print(json_settings)

        # quit()
        exit_on_completion = json_settings["exit_on_completion"]
        infinite_loop = json_settings["infinite_loop"]
        loop_timeout = json_settings["loop_timeout"]
        json_sites = json_config["supported"]
        json_sites = main_helper.process_supported(
            json_config["supported"], args)
        print
        print("Sites:")
        print(json_sites)
        print("-------------------------------------------------------------------")

        domain = json_settings["auto_site_choice"]
        string, site_names = main_helper.module_chooser(domain, json_sites)

        # logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        async def main():
            while True:
                if domain:
                    if site_names:
                        site_name = domain
                    else:
                        print(string)
                        continue
                else:
                    print(string)
                    site_choice = str(input())
                    site_choice = int(site_choice)
                    site_name = site_names[site_choice]
                site_name_lower = site_name.lower()
                api = await main_datascraper.start_datascraper(
                    json_config, site_name_lower
                )
                if api:
                    for a in api.auths:
                        for s in a.subscriptions:
                            dbFiles.append(s.download_info.get(
                                "metadata_locations").get("Posts"))
                    api.close_pools()

                if(len(dbFiles) == 0):
                    process_root(json_sites['onlyfans']
                                 ['settings']['metadata_directories'][0])

                CombineFiles()

                if exit_on_completion:
                    print("Now exiting.")
                    exit(0)
                elif not infinite_loop:
                    print("Input anything to continue")
                    input()
                elif loop_timeout:
                    print("Pausing scraper for " + loop_timeout + " seconds.")
                    time.sleep(int(loop_timeout))
                    #json_settings = json_config["settings"]

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
except Exception as e:
    print(traceback.format_exc())
    input()
