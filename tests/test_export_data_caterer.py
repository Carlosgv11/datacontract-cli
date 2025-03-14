import os
import sys

import yaml
from typer.testing import CliRunner

from datacontract.cli import app
from datacontract.export.data_caterer_converter import to_data_caterer_generate_yaml
from datacontract.model.data_contract_specification import DataContractSpecification


def test_cli():
    runner = CliRunner()
    result = runner.invoke(app, ["export", "./fixtures/export/datacontract.yaml", "--format", "data-caterer"])
    assert result.exit_code == 0


def test_to_data_caterer():
    data_contract = DataContractSpecification.from_string(
        read_file("fixtures/data-caterer/export/datacontract_nested.yaml")
    )
    expected_data_caterer_model = _get_expected_data_caterer_yaml("s3://covid19-lake/enigma-jhu/json/*.json")

    data_caterer_yaml = to_data_caterer_generate_yaml(data_contract, None)
    result = yaml.safe_load(data_caterer_yaml)

    assert result == yaml.safe_load(expected_data_caterer_model)


def test_to_data_caterer_with_server():
    data_contract = DataContractSpecification.from_string(
        read_file("fixtures/data-caterer/export/datacontract_nested.yaml")
    )
    expected_data_caterer_model = _get_expected_data_caterer_yaml("s3://covid19-lake-prod/enigma-jhu/json/*.json")

    data_caterer_yaml = to_data_caterer_generate_yaml(data_contract, "s3-json-prod")
    result = yaml.safe_load(data_caterer_yaml)

    assert result == yaml.safe_load(expected_data_caterer_model)


def _get_expected_data_caterer_yaml(path: str):
    return f"""
name: Orders Unit Test
steps:
- name: orders
  type: json
  options:
    path: {path}
  fields:
  - name: order_id
    type: string
    options:
      isUnique: true
      minLen: 8
      maxLen: 10
      regex: ^B[0-9]+$
      isPrimaryKey: true
  - name: order_total
    type: decimal
    options:
      min: 0
      max: 1000000
  - name: amount
    type: double
  - name: customer_id
    type: integer
  - name: customer_id_int
    type: integer
  - name: customer_id_long
    type: long
  - name: customer_id_float
    type: float
  - name: customer_id_number
    type: double
  - name: customer_id_numeric
    type: double
  - name: created_date
    type: date
  - name: created_ts
    type: timestamp
  - name: created_ts_tz
    type: timestamp
  - name: created_ts_ntz
    type: timestamp
  - name: order_status
    type: string
    options:
      oneOf:
      - pending
      - shipped
      - delivered
  - name: address
    type: struct
    fields:
    - name: street
      type: string
    - name: city
      type: string
  - name: tags
    type: array
    options:
      arrayType: string
  - name: tags_int
    type: array
    options:
      arrayType: integer
"""


def read_file(file):
    if not os.path.exists(file):
        print(f"The file '{file}' does not exist.")
        sys.exit(1)
    with open(file, "r") as file:
        file_content = file.read()
    return file_content
