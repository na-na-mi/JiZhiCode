import shelve
import datetime

allUsers=dict()
allBlogs=dict()
enum=('pu','pr','se')
#抽象用户对象
class User:
    def __init__(self,name,password,description=None):
        self.__blogs__=[]
        self.__name__=name   #用户姓名
        self.__password__=password   #用户密码
        self.__description__=description 
        self.__friendNames__=[]    #好友列表

    #访问自己的Blog
    def getOwnBlogsContent(self):
        strBlogs=''
        for id in self.__blogs__:
            strBlogs+=allBlogs.get(id).printBlogs()
        return strBlogs
    #访问朋友的Blog
    def getFriendsBlogsContent(self):
        strBlog=''
        for userKey in allUsers:
            if userKey==self.__name__:
                continue
            for blogKey in allUsers.get(userKey).getBlogs():
                if allBlogs.get(blogKey).__attribute__=='pu':
                    strBlog+="name:"+userKey+"\n"+allBlogs.get(blogKey).printBlogs()
                elif allBlogs.get(blogKey).__attribute__=='pr' and userKey in self.getFriend():
                    strBlog+="name:"+userKey+"\n"+allBlogs.get(blogKey).printBlogs()
        return strBlog

    #得到blogs
    def getBlogs(self):
        return self.__blogs__
    #写blog
    def writeBlog(self,newId,title,content,attribute):
        self.__blogs__.append(newId)
        new_Blog=Blog(newId,title,content,attribute)
        allBlogs.update({newId:new_Blog})
    def addFriend(self,name):
        self.__friendNames__.append(name)

    def delFriend(self,name):
        self.__friendNames__.remove(name)

    def getFriend(self):
       return self.__friendNames__

    def getPassWord(self):
        return self.__password__


    def getFriendsInfo(self):
        friendsInfo=''
        for userKey in allUsers:
            if self.__name__ in allUsers.get(userKey).getFriend() and userKey in self.getFriend():
                friendsInfo+=userKey
            elif self.__name__ in allUsers.get(userKey).getFriend() and userKey not in self.getFriend():
                 friendsInfo+="+"+userKey
            elif self.__name__ not in allUsers.get(userKey).getFriend() and userKey  in self.getFriend():
                 friendsInfo+="-"+userKey
        return friendsInfo

#抽象Blog对象
class Blog:
    def __init__(self,id,title,content,attribute):
        self.__id__=id  #Blog的id
        self.__title__=title #Blog的标题
        self.__content__=content #Blog的内容
        self.__attribute__ =attribute #Blog的可见
        self.__datetime__=datetime.datetime.now().strftime("%Y-%m-%d,%A,%d. %B %I:%M%p") #Blog的日期

       #Blog内容的取出
    def printBlogs(self):
        all_Content ="id:"+str(self.__id__)+'\n'+"title:"+self.__title__+"\n"+"内容:"+"\n"+"  "+self.__content__+"\n"+"可见:"+self.__attribute__ +"\n"+"日期："+str(self.__datetime__)
        return all_Content

#开始界面菜单
def printMain():
    print("1,注册")
    print("2,登录")
    print("3,退出")

#1、注册用户
def Enroll():
    while True:
        name=input("请输入长度不超过20，并仅包含英文字母和数字的用户名：")
        if len(name)>20:
            print("用户名长度超出20.")
        elif  allUsers.get(name)!=None:
            print("该用户名已经存在。")
        else:
            break
    while True:
        password=input("请输入6个数字作为密码：")
        if len(password)<6:
            print("密码的长度不能小于6位。")
        else:
            password=eval(password)
            break
    use=User(name,password)
    allUsers.update({name:use})
    print("注册成功！！！")

#2、1登录二级界面菜单
def printMainTwo():
    print("1、显示好友用户名")
    print("2、添加朋友")
    print("3、删除朋友")
    print("4、显示朋友圈信息")
    print("5、添加日志信息")
    print("6、显示历史日志信息")
    print("7、显示朋友日志")
    print("8、退出")

#2、2显示所有用户名函数
def printUser(user):
    list1=user.getFriend()
    if len(list1)==0:
        print("好友列表为空。")
    else:
        print(list1)

#2、3添加好友函数
def addFriend(user):
    name_Friend=input("请输入好友名称:")
    if allUsers.get(name_Friend)==None:
        print("该用户不存在。")
    elif name_Friend in user.getFriend():
        print("该好友已在你的好友列表中。")
    else:
        user.addFriend(name_Friend)
        print("好友添加成功")
#2、4删除好友好友
def delFriend(user):
    name_Friend=input("请输入好友名称:")
    if allUsers.get(name_Friend)==None:
        print("该用户不存在。")
    else:
        user.delFriend(name_Friend)
        print("删除成功")

#2、5显示朋友圈信息函数
def friendInfo(user):
    print(user.getFriendsInfo())

#2、6添加Blog
def addBlog(user):
    while True:
        attribute=input("输入Blog对谁可见：(所有人可见(pu)、仅朋友可见(pr)和仅自己可见(se)：")
        if attribute not in enum:
            print("输入有误")
        else:
            break
    title=input("输入博客标题：")
    content=input("输入blog的内容：")
    user.writeBlog(len(allBlogs),title,content,attribute)

#2、7显示历史日志信息
def printBlog(user):
    print(user.getOwnBlogsContent())
#2、8显示朋友日志函数
def printFriendsBlog(user):
    print(user.getFriendsBlogsContent())
#1、2二级登录主函数
def mainTwo(user):
    while True:
        printMainTwo()
        num=eval(input())
        if num==1:
            printUser(user)
        elif num==2:
            addFriend(user)
        elif num==3:
            delFriend(user)
        elif num==4:
            friendInfo(user)
        elif num==5:
            addBlog(user)
        elif num==6:
             printBlog(user)
        elif num==7:
            printFriendsBlog(user)
        elif num==8:
            break

#1、2用户登录函数
def Login():
    while True:
        name=input("请输入用户名:")
        password=eval(input("请输入密码:"))
        if allUsers.get(name)==None:
            print("输入的用户不存在。")
        elif allUsers.get(name).getPassWord()!=password:
            print(allUsers.get(name).getPassWord())
            print("输入的密码错误。")
        else:
             print("登录成功！！！")
             return name
    return None        
#程序主函数入口
def main():
    while True:
        printMain()
        operate_One=eval(input())
        if(operate_One==1):
            Enroll()
        elif(operate_One==2):
            flag=Login()
            if flag!=None:
               mainTwo(allUsers.get(flag))

        elif(operate_One==3):
            break




#基于shelve模块读取
      # 打开一个文件
try:
    db1 = shelve.open('users_blogs.db')
    allUsers.update(db1['users'])
    allBlogs.update(db1['blogs'])
except:
    allUsers = {}
    allBlogs = {}
    print('except')

#基于shelve模块保存
def SaveDate():
    db1['users']=allUsers
    db1['blogs']=allBlogs
    db1.close()

main()
SaveDate()