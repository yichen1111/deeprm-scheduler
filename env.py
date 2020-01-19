
import os
import json
import numpy as np
from PIL import Image

class Node(object):
    """Node"""
    def __init__(self, resources, duration, label):
        self.resources = resources
        self.duration = duration
        self.label = label
        self.dimension = len(resources)
        self.state_matrices = [np.full((duration, resource), 255, dtype=np.uint8) for resource in resources]
        self._state_matrices_capacity = [[resource]*duration for resource in resources]

    def schedule(self, task):
        start_time = self._satisfy(self._state_matrices_capacity, task.resources, task.duration)
        if start_time == -1:
            return False
        else:
            for i in range(0, task.dimension):
                self._occupy(self.state_matrices[i], self._state_matrices_capacity[i], task.resources[i], task.duration, start_time)
            return True

    def timestep(self):
        for i in range(0, self.dimension):
            temp = np.delete(self.state_matrices[i], (0), axis=0)
            temp = np.append(temp, np.array([[255 for x in range(0, temp.shape[1])]]), axis=0)
            self.state_matrices[i] = temp
        for i in range(0, self.dimension):
            self._state_matrices_capacity[i].pop(0)
            self._state_matrices_capacity[i].append(self.resources[i])

    def _satisfy(self, capacity_matrix, required_resources, required_duration):
        p1 = 0
        p2 = 0
        duration_bound = min([len(capacity) for capacity in capacity_matrix])
        while p1 < duration_bound and p2 < required_duration:
            if False in [capacity_matrix[i][p1] >= required_resources[i] for i in range(0, len(required_resources))]:
                p1 = p1 + 1
                p2 = 0
            else:
                p1 = p1 + 1
                p2 = p2 + 1
        if p2 == required_duration:
            return p1 - required_duration
        else:
            return -1

    def _occupy(self, state_matrix, state_maxtrix_capacity, required_resource, required_duration, start_time):
        for i in range(start_time, start_time+required_duration):
            for j in range(0, required_resource):
                state_matrix[i, len(state_matrix[i])-state_maxtrix_capacity[i]+j] = 0
            state_maxtrix_capacity[i] = state_maxtrix_capacity[i] - required_resource

    def __repr__(self):
        return 'Node(state_matrices={0}, label={1})'.format(self.state_matrices, self.label)

class Environment(object):
    """Environment"""
    def __init__(self, nodes, queue_size, backlog_size):
        self.nodes = nodes
        self.queue_size = queue_size
        self.backlog_size = backlog_size
        self.queue = []
        self.backlog = []

    def plot(self):
        if not os.path.exists('__state__'):
            os.makedirs('__state__')
        for node in self.nodes:
            for i in range(0, node.dimension):
                Image.fromarray(node.state_matrices[i]).save('__state__/{0}_resource{1}.png'.format(node.label, i+1))

    def __repr__(self):
        return 'Environment(nodes={0}, queue={1}, backlog={2})'.format(self.nodes, self.queue, self.backlog)

def load_environment():
    """load environment from conf/env.conf.json"""
    with open('conf/env.conf.json', 'r') as fr:
        data = json.load(fr)
        nodes = []
        label= 0
        for node_json in data['nodes']:
            label = label + 1
            nodes.append(Node(node_json['resource_capacity'], node_json['duration_capacity'], 'node' + str(label)))
        return Environment(nodes, data['queue_size'], data['backlog_size'])