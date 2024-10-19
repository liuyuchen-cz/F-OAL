import numpy as np
from torchvision import datasets, transforms
from continuum.data_utils import create_task_composition, load_task_with_labels
from continuum.dataset_scripts.dataset_base import DatasetBase
from continuum.non_stationary import construct_ns_multiple_wrapper, test_ns
from PIL import Image

class FOOD101(DatasetBase):
    def __init__(self, scenario, params):
        dataset = 'food101'
        if scenario == 'ni':
            num_tasks = len(params.ns_factor)
        else:
            num_tasks = params.num_tasks

        super(FOOD101, self).__init__(dataset, scenario, num_tasks, params.num_runs, params)

    def download_load(self):
        train = datasets.Food101(root=self.root, split='train', download=True)
        test = datasets.Food101(root=self.root, split='test', download=True)
        self.train_data = []
        self.train_label = []
        self.test_data = []
        self.test_label = []
        for image, label in train:
            image = image.resize((224, 224), Image.Resampling.LANCZOS)
            self.train_data.append(image)
            self.train_label.append(label)
        self.train_data = np.array(self.train_data)
        self.train_label = np.array(self.train_label)

        for image, label in test:
            image = image.resize((224, 224), Image.Resampling.LANCZOS)
            self.test_data.append(image)
            self.test_label.append(label)
        self.test_data = np.array(self.test_data)
        self.test_label = np.array(self.test_label)

        # print(dataset_train.shape)

    def setup(self):
        if self.scenario == 'ni':
            self.train_set, self.val_set, self.test_set = construct_ns_multiple_wrapper(self.train_data,
                                                                                        self.train_label,
                                                                                        self.test_data, self.test_label,
                                                                                        self.task_nums, 32,
                                                                                        self.params.val_size,
                                                                                        self.params.ns_type, self.params.ns_factor,
                                                                                        plot=self.params.plot_sample)
        elif self.scenario == 'nc':
            self.task_labels = create_task_composition(class_nums=101, num_tasks=self.task_nums, fixed_order=self.params.fix_order)
            self.test_set = []
            for labels in self.task_labels:
                x_test, y_test = load_task_with_labels(self.test_data, self.test_label, labels)
                self.test_set.append((x_test, y_test))
        else:
            raise Exception('wrong scenario')

    def new_task(self, cur_task, **kwargs):
        if self.scenario == 'ni':
            x_train, y_train = self.train_set[cur_task]
            labels = set(y_train)
        elif self.scenario == 'nc':
            labels = self.task_labels[cur_task]
            x_train, y_train = load_task_with_labels(self.train_data, self.train_label, labels)
        return x_train, y_train, labels

    def new_run(self, **kwargs):
        self.setup()
        return self.test_set

    def test_plot(self):
        test_ns(self.train_data[:10], self.train_label[:10], self.params.ns_type,
                                                         self.params.ns_factor)
