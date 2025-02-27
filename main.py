import sys
 
# sys.stdin = open('input.txt', 'r')

# I=lambda: map(int, input().split())

for _ in range(int(input())):
    s = input(); has = 0
    # print(s)
    for i in range(0,len(s)-1,1):
        if s[i] == s[i+1] and has == 0:
            print(1); has = 1; break
    if has == 0:
        print(len(s))
        
    # ans = ""; has = 0
    # for i in range(len(s)-1,0,-1):
    #     # print(s[i],s[i-1])
    #     if s[i] == 's' and s[i-1] == 'u' and  has == 0:
    #         ans += 'i'; has = 1
    #     else:
    #         ans += s[i-1]
    # print(ans[-1::-1])
    
