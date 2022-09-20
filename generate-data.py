import json
import random
import sys
import dateutil.parser
import datetime


class LabStepGenerator():
    def __init__(self, step, save_path):
        self.step = step
        self.save_path = save_path
        self.now = None
        self.generated_step_data = []

    def _add_data_jitter(self, point_data, jitter_pct):
        point_data = point_data.copy()
        for key in point_data.keys():
            if type(point_data[key]) != type('mystring'):
                jitter = point_data[key] * jitter_pct
                point_data[key] += random.gauss(0, jitter)
        return point_data

    def _write_step_to_json(self):
        filename = f"{self.save_path}/{self.step['name']}.json"
        with open(filename, 'w') as fw:
            json_str = json.dumps(self.generated_step_data, indent=4)
            fw.write(json_str)

    def _generate_sample_for_devices(self):
        for device in self.step['devices']:
            device['point_data'] = self._add_data_jitter(device['point_data'],
                                                         self.step['jitter'])
            device['date'] = self.now.isoformat()
            self.generated_step_data.append(device.copy())

    def generate(self):
        self.now = dateutil.parser.parse(self.step['datetime'])
        time_delta = datetime.timedelta(0, 0, 0, 0, self.step['mins_between'])
        for _ in range(self.step['num_samples']):
            self._generate_sample_for_devices()
            self.now += time_delta
        self._write_step_to_json()


class LabGenerator():
    def __init__(self, lab_name):
        self.lab_name = lab_name
        self.config_steps = []

        self._load_simulator_config()

    def _load_simulator_config(self):
        with open('simulator-generator.json') as f:
            simulator_config = json.load(f)
            self.config_steps = simulator_config[self.lab_name]

    def generate(self):
        for step in self.config_steps:
            step_generator = LabStepGenerator(step, self.lab_name)
            step_generator.generate()


def main(lab_name):
    lab_generator = LabGenerator(lab_name)
    lab_generator.generate()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: generate-data.py <lab>')
        sys.exit()
    main(sys.argv[1])
