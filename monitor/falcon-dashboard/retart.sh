#!/bin/bash
sudo docker stop falcon-dashboard-self && sudo docker rm falcon-dashboard-self && sudo docker build . -t falcon-dashboard:local && bash start


