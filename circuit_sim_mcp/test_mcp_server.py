from circuit_sim_mcp import circuit
from circuit_sim_mcp import simulator
from circuit_sim_mcp import server_basic
import numpy as np

sim_server = server_basic.CircuitSimServer()

example = {
                        "name": "rc_lowpass_example",
                        "components": [
                            {"name": "V1", "component_type": "voltage_source", "nodes": ["input", "gnd"], "voltage": 1.0, "source_type": "AC"},
                            {"name": "R1", "component_type": "resistor", "nodes": ["input", "output"], "resistance": 1000.0},
                            {"name": "C1", "component_type": "capacitor", "nodes": ["output", "gnd"], "capacitance": 1e-6}
                        ],
                        "expected_output": {"input": 1.0, "output": 1.0, "gnd": 0.0},
                        "description": "RC low-pass filter, 1kΩ resistor, 1µF capacitor (DC analysis: output = input)"
                    }
c1 = circuit.Circuit('rc_lowpass')
for comp_data in example["components"]:
    component = circuit.Component.from_dict(comp_data)
    c1.add_component(component)

simulator = simulator.CircuitSimulator()
spice_circuit = simulator._create_spice_circuit(c1)
print(f'Spice circuit: {spice_circuit}')
spice_simulator = spice_circuit.simulator(temperature=25, nominal_temperature=25)

from PySpice.Spice.Netlist import Circuit as PySpiceCircuit
from PySpice.Spice.Netlist import Netlist
from PySpice.Unit import *

start_freq = 10.0
stop_freq = 100000.0
num_points = 100
analysis = spice_simulator.ac(
                start_frequency=start_freq@u_Hz,
                stop_frequency=stop_freq@u_Hz,
                number_of_points=num_points,
                variation='dec'
            )

results = analysis
data = {"frequency": []}
data["frequency"] = [float(f) for f in results.frequency]

output_nodes =  list(c1.get_nodes())
for node in output_nodes:
    if hasattr(results, node):
        node_data = getattr(results, node)
        if hasattr(node_data, 'magnitude'):
            data[f"{node}_magnitude"] = [float(m) for m in node_data.magnitude]
        else:
            print(f'node data {node} has no attribute magnitude')
            magnitude = np.abs(node_data)
            data[f"{node}_magnitude"] = [float(m) for m in magnitude]
        if hasattr(node_data, 'phase'):
            data[f"{node}_phase"] = [float(p) for p in node_data.phase]
        else:
            print(f'node data {node} has no attribute phase')
            phase_radians = np.angle(node_data)
            #phase_degrees = np.degrees(node_data)
            data[f"{node}_phase"] = [float(p) for p in phase_radians]
            #data[f"{node}_phase_degrees"] = [float(p) for p in phase_degrees]
    else:
    	print(f"Node '{node}' not found in AC analysis results")

for k in data.keys():
    print(f'{k}: items {len(data[k])}')
print(f'Direct pyspice simulatopn result data: {data}')

data = simulator.simulate_ac(c1, start_freq, stop_freq, num_points, ['output', 'input'])
print(f'Data summary:')
for k in data.data.keys():
    print(f'{k}: items {len(data.data[k])}')
print(f'MCP simulation: {data}')