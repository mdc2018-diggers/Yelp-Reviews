import pandas as pd
import os
import json
import math
import subprocess
import itertools

class Fixups:
    class Csv:
        pass

    class Json:
        @staticmethod
        def business(obj):
            obj['is_open'] = bool(obj['is_open'])
            obj['categories'] = obj['categories'].split(', ') if obj['categories'] is not None else []

            def pretty_hour(hour):
                hour, min = hour.split(':')
                return '{hour}:{min}'.format(hour=hour, min=min.ljust(2, "0"))
            def pretty_hour_range(hours):
                return tuple(pretty_hour(h) for h in hours.split('-'))

            if obj['hours'] is not None:
                obj['hours'] = {
                    k: pretty_hour_range(v)
                    for k,v in obj['hours'].items()
                }
            return obj



def _multiple(f):
    def wrapper(*args, **kwargs):
        if len(args) == 0:
            return None
        elif len(args) == 1:
            return f(args[0], **kwargs)
        else:
            return tuple(f(arg, **kwargs) for arg in args)
    return wrapper

def _dataframe(f):
    def wrapper(*args, **kwargs):
        dataframe = kwargs.pop('dataframe', False)
        gen = f(*args, **kwargs)
        if dataframe:
            return pd.DataFrame(gen)
        else:
            return gen
    return wrapper

def _batches(f):
    def wrapper(*args, **kwargs):
        batch_size = kwargs.pop('batch_size', None)
        gen = f(*args, **kwargs)
        if batch_size is not None:
            while True:
                chunk = list(itertools.islice(gen, batch_size))
                if len(chunk) == 0:
                    break
                else:
                    yield chunk
        else:
            yield from gen
    return wrapper

def _limit_offset(f):
    def wrapper(*args, **kwargs):
        limit = kwargs.pop('limit', -1)
        offset = kwargs.pop('offset', 0)

        for i, x in enumerate(f(*args, **kwargs)):
            if limit >= 0 and i > limit + offset:
                break
            if i > offset:
                yield x
    return wrapper


def _map_and_filter(f):
    def wrapper(*args, **kwargs):
        map = kwargs.pop('map', lambda x: x)
        attrs = kwargs.pop('attrs', None)
        filter = kwargs.pop('filter', lambda x: True)
        for x in f(*args, **kwargs):
            x = map(x)
            if not filter(x):
                continue

            if isinstance(attrs, str):
                x = x[attrs]
            elif attrs is not None:
                x = tuple(x[attr] for attr in attrs)

            yield x
    return wrapper


def _repeat(f):
    def wrapper(*args, **kwargs):
        repeat = kwargs.pop('repeat', False)
        if isinstance(repeat, bool):
            if repeat:
                while True:
                    yield from f(*args, **kwargs)
            else:
                yield from f(*args, **kwargs)
        elif isinstance(repeat, int):
            for i in range(repeat):
                yield from f(*args, **kwargs)
        else:
            raise Exception('Invalid repeat argument')
    return wrapper

def _get_dataset_file(name):
    dataset_dir = 'Datasets'
    filename = 'yelp_academic_dataset_' + name + '.json'
    file = os.path.join(dataset_dir, filename)
    if not os.path.exists(file):
        print('Fetching dataset ' + name + '...')
        subprocess.check_call([
            'kaggle', 'datasets', 'download',
            '--force',
            'yelp-dataset/yelp-dataset',
            '-f', filename,
            '-p', dataset_dir
        ])
        subprocess.check_call([
            'unzip',
            '-x', file + '.zip',
            '-d', dataset_dir
        ])
        subprocess.check_call(['rm', file + '.zip'])
    return file

@_multiple
@_dataframe
@_batches
@_limit_offset
@_map_and_filter
@_repeat
def read(name):
    fixup = getattr(Fixups.Json, name, lambda x: x)
    with open(_get_dataset_file(name), encoding="utf-8") as stream:
        for line in stream:
            yield fixup(json.loads(line))
