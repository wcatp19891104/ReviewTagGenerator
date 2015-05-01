__author__ = 'wangzaicheng'

from Prepare.DataClean.temp import GeneralUsage_pb2


def Mapper(key, value):
    i = 0
    print value
    curr_obj = GeneralUsage_pb2.GeneralUsagePro()
    curr_obj.MergeFromString(value)
    print curr_obj.ipAddress
    print i
    i += 1
    yield value, 0

def reducer(key, value):
    yield key, 0


if __name__ == "__main__":
    import dumbo
    dumbo.run(Mapper, reducer, combiner=reducer)


