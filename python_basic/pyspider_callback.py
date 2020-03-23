# -*- coding: utf-8 -*-

"""
从pyspider中关于回调函数的写法，应用于自己关于爬虫的写法中
参考写法：pyspider.libs.base_handler
"""

import six
import requests
from lxml import etree
from abc import abstractmethod, ABCMeta

from functools import wraps


def reported(message : str):
    """A decorator for reporting function status
    Args:
        message: str
    """
    def report(func):
        wraps(func)
        def wrapper(*args, **kwargs):
            print("start  " + message + "...")
            res = func(*args, **kwargs)
            print("finish  " + message + "...")
            return res
        return wrapper
    return report

class BaseHandler(metaclass=ABCMeta):
    config_dict = {

    }

    def __init__(self):
        pass

    @abstractmethod
    def run(self):
        """main function, run your spider, you can inhert this method"""
        pass

    @abstractmethod
    def detail_page(self, response):
        """Abstract method: Parsing a single web page, you can inherit this method
        return a dict object
        Args:
            response:
        return:
            data: dict
        """

    def _crawl(self, url, **kwargs):
        """callback"""
        if kwargs.get("callback"):
            callback = kwargs["callback"]
            if isinstance(callback, six.string_types) and hasattr(self, callback):
                func = getattr(self, callback)
            elif six.callable(callback) and six.get_method_self(callback) is self:
                func =  callback
                kwargs["callback"] = func.__name__
            else:
                raise NotImplemented("self.%s() not implemented" % callback)

        response = requests.get(url, headers=self.config_dict.get("headers", None)).content
        response = etree.HTML(response)
        return func(response)


    def crawl(self, url, **kwargs):
        """can define page turning, multi-level page crawling strategy"""
        if isinstance(url, six.string_types):
            return self._crawl(url, **kwargs)
        elif hasattr(url, "__iter__"):
            result = []
            for each in url:
                result.append(self._crawl(each, **kwargs))
            return result

    @abstractmethod
    def on_start(self, result):
        pass

if __name__ == '__main__':
    import codecs

    class SpiderWuTongBao(BaseHandler):

        def __init__(self):
            super(BaseHandler, self).__init__()

        @reported('running main function')
        def run(self):
            urls = ["https://bx.baoxianjie.net/hb/{}.html".format(i) for i in range(400)]
            result = []
            for url in urls:
                data = self.crawl(url, callback=self.detail_page)
                result.append(data)
            self.on_result(result, 'test.json')

        def detail_page(self, response):
            disease = response.xpath("/html/body/div[5]/div[2]/div[1]/span/text()")
            Insurance_result = response.xpath('/html/body/div[5]/div[2]/div[2]/div[1]/ul/li/text()')
            Discription = response.xpath('/html/body/div[5]/div[2]/div[2]/div[2]/ul/li/text()')
            CheckItem = response.xpath('/html/body/div[5]/div[2]/div[2]/div[3]/ul/li/text()')

            def mapper(item):
                if isinstance(item, list):
                    if len(item) == 0:
                        return ""
                    elif len(item) == 1:
                        return item[0].replace('\n', "")
                    elif len(item) > 1:
                        return "".join(item).replace("\n", "")
                elif isinstance(item, six.string_types):
                    return item.replace("\n", "")

            return {"Disease": mapper(disease),
                    'Insurance_result': mapper(Insurance_result),
                    'Discription': mapper(Discription),
                    'CheckItem': mapper(CheckItem),
                    }

        @reported('writing into file')
        def on_result(self, result, output):
            import json
            with codecs.open(output, 'w', encoding='utf-8') as fb:
                json.dump(result, fb, ensure_ascii=False)


    spider = SpiderWuTongBao()
    spider.run()