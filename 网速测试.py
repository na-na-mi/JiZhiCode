
import speedtest


def main():
    s = speedtest.Speedtest()
    s.get_best_server()
    dl = s.download()
    ul = s.upload()
    print(f"下载速度：{dl / 1024 / 1024:.2f}Mb")
    print(f"上传速度：{ul / 1024 / 1024:.2f}Mb")


if __name__ == '__main__':
    print("测试中。。。请耐心等候")
    main()
