
import os
import copy
import json
import sys

import torch
from dgl import DGLGraph
from tqdm import tqdm

from data_loader.batch_graph import GGNNBatchGraph
from utils import load_default_identifiers, initialize_batch, debug

import random


class DataEntry:
    def __init__(self, datset, num_nodes, features, edges, target, function_name, slice_path):
        self.dataset = datset
        self.num_nodes = num_nodes
        self.target = target
        self.graph = DGLGraph()
        self.features = torch.FloatTensor(features)
        self.slice_path = slice_path
        self.function_name = function_name
        self.graph.add_nodes(self.num_nodes, data={"features": self.features})
        for s, _type, t in edges:
            etype_number = self.dataset.get_edge_type_number(_type)
            self.graph.add_edge(s, t, data={"etype": torch.LongTensor([etype_number])})


class DataSet:
    def __init__(self, train_src, valid_src=None, test_src=None, batch_size=32, n_ident=None, g_ident=None, l_ident=None):
        self.train_examples = []
        self.valid_examples = []
        self.test_examples = []
        self.train_batches = []
        self.valid_batches = []
        self.test_batches = []
        self.batch_size = batch_size
        self.edge_types = {}
        self.max_etype = 0
        self.feature_size = 100
        self.n_ident, self.g_ident, self.l_ident= load_default_identifiers(n_ident, g_ident, l_ident)
        self.read_dataset(train_src, valid_src, test_src)
        self.initialize_dataset()

    def initialize_dataset(self):
        self.initialize_train_batch()
        self.initialize_valid_batch()
        self.initialize_test_batch()

    def read_dataset(self, train_src:dict, valid_src:dict, test_src:dict):
        debug('Reading Train File! ')
        if len(train_src) != 0:
            for function_name, slice_path_list in tqdm(train_src.items()):
                for slice_path in slice_path_list:
                    with open(slice_path, 'r') as fp:
                        pdg = json.load(fp)
                        if len(pdg[self.n_ident]) == 0 or len(pdg[self.n_ident]) < 9:
                            continue
                        example = DataEntry(datset=self, num_nodes=len(pdg[self.n_ident]), features=pdg[self.n_ident],
                                        edges=pdg[self.g_ident], target=pdg[self.l_ident], function_name=function_name, slice_path=slice_path)
                        self.train_examples.append(example)
        
        debug('Reading Valid File! ')
        if len(valid_src) != 0:
            for function_name, slice_path_list in tqdm(valid_src.items()):
                for slice_path in slice_path_list:
                    with open(slice_path, 'r') as fp:
                        pdg = json.load(fp)
                        if len(pdg[self.n_ident]) == 0 or len(pdg[self.n_ident]) < 9:
                            continue
                        example = DataEntry(datset=self, num_nodes=len(pdg[self.n_ident]), features=pdg[self.n_ident],
                                        edges=pdg[self.g_ident], target=pdg[self.l_ident], function_name=function_name, slice_path=slice_path)
                        self.valid_examples.append(example)
        
        debug('Reading Test File! ')
        if len(test_src) != 0:
            for function_name, slice_path_list in tqdm(test_src.items()):
                for slice_path in slice_path_list:
                    with open(slice_path, 'r') as fp:
                        pdg = json.load(fp)
                        if len(pdg[self.n_ident]) == 0 or len(pdg[self.n_ident]) < 9:
                            continue
                        example = DataEntry(datset=self, num_nodes=len(pdg[self.n_ident]), features=pdg[self.n_ident],
                                        edges=pdg[self.g_ident], target=pdg[self.l_ident], function_name=function_name, slice_path=slice_path)
                        self.test_examples.append(example)

    # def read_dataset(self, test_src, train_src, valid_src):
    #     if train_src is not None:
    #         debug('Reading Train File!',train_src)
    #         with open(train_src) as fp:
    #             path_list = fp.readlines()
    #             for path in tqdm(path_list):
    #                 with open(path.strip(), 'r') as json_file:
    #                     pdg = json.load(json_file)
    #                     if len(pdg[self.n_ident]) == 0 or len(pdg[self.n_ident]) < 9:
    #                         continue
    #                     example = DataEntry(datset=self, num_nodes=len(pdg[self.n_ident]), features=pdg[self.n_ident],
    #                                     edges=pdg[self.g_ident], target=pdg[self.l_ident])
    #                     if self.feature_size == 0:
    #                         self.feature_size = example.features.size(1)
    #                         debug('Feature Size %d' % self.feature_size)
    #                     self.train_examples.append(example)

    #     if valid_src is not None:
    #         debug('Reading Validation File!')
    #         with open(valid_src) as fp:
    #             valid_data = json.load(fp)
    #             for entry in tqdm(valid_data.values()):
    #                 if len(entry[self.n_ident]) == 0:
    #                     continue
    #                 if len(entry[self.n_ident]) < 9:
    #                     continue
    #                 example = DataEntry(datset=self, num_nodes=len(entry[self.n_ident]),
    #                                     features=entry[self.n_ident],
    #                                     edges=entry[self.g_ident], target=entry[self.l_ident])
    #                 self.valid_examples.append(example)
    #                 if len(self.valid_examples) == 300:
    #                     break

    #     debug('Reading Test File!',test_src)
    #     with open(test_src) as fp:
    #         path_list = fp.readlines()
    #         for path in tqdm(path_list):
    #             with open(path.strip(), 'r') as json_file:
    #                 pdg = json.load(json_file)
    #                 if len(pdg[self.n_ident]) == 0 or len(pdg[self.n_ident]) < 9:
    #                     continue
    #                 example = DataEntry(datset=self, num_nodes=len(pdg[self.n_ident]), features=pdg[self.n_ident],
    #                                 edges=pdg[self.g_ident], target=pdg[self.l_ident])
    #                 self.test_examples.append(example)

    def get_edge_type_number(self, _type):
        if _type not in self.edge_types:
            self.edge_types[_type] = self.max_etype
            self.max_etype += 1
        return self.edge_types[_type]

    @property
    def max_edge_type(self):
        return self.max_etype

    def initialize_train_batch(self, batch_size=-1):
        if batch_size == -1:
            batch_size = self.batch_size
        self.train_batches = initialize_batch(self.train_examples, batch_size, shuffle=True)
        return len(self.train_batches)
        pass

    def initialize_valid_batch(self, batch_size=-1):
        if batch_size == -1:
            batch_size = self.batch_size
        self.valid_batches = initialize_batch(self.valid_examples, batch_size)
        return len(self.valid_batches)
        pass

    def initialize_test_batch(self, batch_size=-1):
        if batch_size == -1:
            batch_size = self.batch_size
        self.test_batches = initialize_batch(self.test_examples, batch_size)
        return len(self.test_batches)
        pass

    def get_dataset_by_ids_for_GGNN(self, entries, ids):
        taken_entries = [entries[i] for i in ids]
        entries_name = [f'{entries[i].function_name},{entries[i].slice_path}' for i in ids]
        labels = [int(e.target) for e in taken_entries]
        batch_graph = GGNNBatchGraph()
        for entry in taken_entries:
            batch_graph.add_subgraph(copy.deepcopy(entry.graph))
        return batch_graph, torch.LongTensor(labels), entries_name

    def get_next_train_batch(self):
        if len(self.train_batches) == 0:
            self.initialize_train_batch()
        ids = self.train_batches.pop()
        return self.get_dataset_by_ids_for_GGNN(self.train_examples, ids)

    def get_next_valid_batch(self):
        if len(self.valid_batches) == 0:
            self.initialize_valid_batch()
        ids = self.valid_batches.pop()
        return self.get_dataset_by_ids_for_GGNN(self.valid_examples, ids)

    def get_next_test_batch(self):
        if len(self.test_batches) == 0:
            self.initialize_test_batch()
        ids = self.test_batches.pop()
        return self.get_dataset_by_ids_for_GGNN(self.test_examples, ids)