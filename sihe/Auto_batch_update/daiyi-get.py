# -*- coding: UTF-8 -*- 
import os
from AiClothClient import AiClothClient
import subprocess


def show_at_page():
    client = AiClothClient()
    all_deb_list = client.get_al_deb()
    deb_list=[]
    for i in all_deb_list:
        if i.startswith("flaw") or i.startswith("detection"):
            deb_list.append(i)
            push_deb_shell = 'python3 auto_push_deb.py --deb '+ i +' --env prod'
            print(push_deb_shell)
        print()

show_at_page()