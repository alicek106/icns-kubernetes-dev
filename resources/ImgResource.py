from __future__ import print_function
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import docker
from threading import Lock
import threading

mutex = Lock()

class ImgResource:
    __docker_list = ['http://163.180.117.219:50002', 'http://163.180.117.219:50003']
    __semaphore = 0

    def pullImage(self, cli, docker_endpoint, imageName):
        mutex.acquire()
        print('pulling start to %s' % docker_endpoint)
        self.__semaphore = self.__semaphore + 1
        mutex.release()

        cli.pull(imageName)

        mutex.acquire()
        print('end pulling to %s' % docker_endpoint)
        self.__semaphore = self.__semaphore - 1
        mutex.release()

    def distributeImage(self, repo, tag):
        if self.__semaphore is not 0:
            return

        imageName = repo + ':' + tag
        threads = []
        for docker_endpoint in self.__docker_list:
            cli = docker.APIClient(base_url=docker_endpoint)
            images = cli.images()
            image_exist = False
            for image in images:
                if imageName in image['RepoTags']:
                    image_exist = True
            if not image_exist:
                t1 = threading.Thread(target=self.pullImage,
                                      args=([cli, docker_endpoint, imageName]))
                threads.append(t1)
                t1.start()

            else:
                print('image exist in %s!' % docker_endpoint)

        return True

if __name__ == '__main__':
    print(ImgResource().distributeImage('busybox', 'latest'))