# -*- coding: UTF-8 -*- 
import sys 
short_str_dict={}
long_str = sys.stdin.readline()
for i in long_str:
    if i not in short_str_dict.keys():
        short_str_dict[i] = 1
    elif i in short_str_dict.keys():
        short_str_dict[i] += 1
    else:
        pass

short_str_dict.pop("\n")
sort_key =sorted(short_str_dict.iteritems(), key=lambda d:d[0])
short_str_dict.clear()
for i in sort_key:
    short_str_dict[i[0]]=i[1]
    
for_print_str = ""
for i in sorted(short_str_dict.iteritems(), key=lambda d:d[1], reverse = True):
    for_print_str = for_print_str + i[0] + ":" + str(i[1]) + ";"
print(for_print_str)
        






# import sys 
# for line in sys.stdin:
#     a = line.split()
#     print(int(a[0]) + int(a[1]))


# import sys
# if __name__ == "__main__":
#     # 读取第一行的n
#     n = int(sys.stdin.readline().strip())
#     ans = 0
#     for i in range(n):
#         # 读取每一行
#         line = sys.stdin.readline().strip()
#         # 把每一行的数字分隔后转化成int列表
#         values = list(map(int, line.split()))
#         for v in values:
#             ans += v
#     print(ans)



