import os
import sys
import time
from AiClothClient import AiClothClient

def checkKeywordAndMatchDeb(basedir, client, deb_keyword, tag_keyword=None):
    while 1:
        deb_bag_list = client.get_al_deb()
        print ("检测当前包名列表:\n {}".format(deb_bag_list))
        if tag_keyword != None:
            tag_keyword = tag_keyword.lower()
            deb_bag_name = [ deb_bag for deb_bag in deb_bag_list if deb_keyword in deb_bag and tag_keyword in deb_bag.lower() ]
            deb_bag_name = sorted(deb_bag_name, reverse=True)[0]
        else:
            deb_bag_name = [ deb_bag for deb_bag in deb_bag_list if deb_keyword in deb_bag ]
            deb_bag_name = sorted(deb_bag_name, reverse=True)[0]
        try:
            status = os.system("python3 {}/auto_push_deb.py --deb {}  --env prod".format(basedir, deb_bag_name))
        except Exception as e:
            print ("Error: ", e)
        
        if status == 0:
            print ("检查更新 {} 包执行完毕.".format(deb_bag_name))
        else:
            print ("检查更新 {} 包执行失败.\n\n".format(deb_bag_name))
            sys.exit(1)
        time.sleep(600)
        new_deb_bag_list = client.get_al_deb()
        if deb_bag_name in new_deb_bag_list:
            print ("当前 {} 包未发生改变,操作继续... \n".format(deb_keyword))
            continue
        else:
            print ("检测到 {} 包名有更改!".format(deb_keyword))
            print ("新的包名列表:\n {}".format(new_deb_bag_list))
            time.sleep(600)
            break

if __name__ == '__main__':
    client = AiClothClient()
    #client = AiClothClient(base_url=AiClothClient.DEV_SERVER_BASE_URL, cookie_path='dev-cookie.txt')
    client.interactive_login()
    deb_keyword = sys.argv[1]
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    print ("脚本执行目录：", basedir)
    while 1:
        if len(sys.argv) != 3:
            checkKeywordAndMatchDeb(basedir, client, deb_keyword)
        elif len(sys.argv) == 3:
            tag_keyword = sys.argv[2]
            checkKeywordAndMatchDeb(basedir, client, deb_keyword, tag_keyword)
