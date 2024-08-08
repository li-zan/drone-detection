from types import SimpleNamespace


class IterableSimpleNamespace(SimpleNamespace):
    """IterableSimpleNamespace 是 SimpleNamespace 的扩展类，添加了可迭代功能并支持使用 dict() 和 for 循环。"""

    def __iter__(self):
        """返回命名空间属性的键值对迭代器。"""
        return iter(vars(self).items())

    def __str__(self):
        """返回对象的可读字符串表示形式。"""
        return "\n".join(f"{k}={v}" for k, v in vars(self).items())

    def __getattr__(self, attr):
        """自定义属性访问错误消息。"""
        name = self.__class__.__name__
        raise AttributeError(
            f"""
            '{name}' 对象没有属性 '{attr}'。检查配置文件(config.yaml)中是否含有该配置。
            """
        )

    def get(self, key, default=None):
        """如果存在，则返回指定键的值；否则返回默认值。"""
        return getattr(self, key, default)
