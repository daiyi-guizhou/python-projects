from AiClothClient import AiClothClient, MachineInfo
import json

if __name__ == '__main__':
    # client = AiClothClient(base_url='http://localhost:8081')
    client = AiClothClient()
    client.interactive_login()

    # print("Machine Alias:", client.get_machine_alias())

    for m in client.get_machine_list()['machines']:
        m = MachineInfo(m)
        print(m.getMachineId(), m.getDisplayName())
        print(m.getTags())
        print(m.keys())
        print('-' * 30)

    # test_machine_id = '0C-9D-92-CA-EC-8C' # 60 ceshiji
    # response = client.get_config_yaml(test_machine_id)
    # # note that response['Content'] is still a string object in json format, please call json.loads(response['Content']) to pharse as an object
    # print("config.yaml:", response['Content'])

    # content = json.loads(response['Content'])
    # new_content = json.dumps(content)
    # client.upload_config_yaml(test_machine_id, new_content)

    print('done')



