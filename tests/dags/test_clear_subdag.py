# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import datetime
import warnings

import pytest

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.subdag import SubDagOperator

pytestmark = pytest.mark.db_test


def create_subdag_opt(main_dag):
    subdag_name = "daily_job"
    subdag = DAG(
        dag_id=f"{dag_name}.{subdag_name}",
        start_date=start_date,
        schedule=None,
        max_active_tasks=2,
    )
    BashOperator(bash_command="echo 1", task_id="daily_job_subdag_task", dag=subdag)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"This class is deprecated\. Please use `airflow\.utils\.task_group\.TaskGroup`\.",
        )
        return SubDagOperator(
            task_id=subdag_name,
            subdag=subdag,
            dag=main_dag,
        )


dag_name = "clear_subdag_test_dag"

start_date = datetime.datetime(2016, 1, 1)

dag = DAG(dag_id=dag_name, max_active_tasks=3, start_date=start_date, schedule="0 0 * * *")

daily_job_irrelevant = BashOperator(
    bash_command="echo 1",
    task_id="daily_job_irrelevant",
    dag=dag,
)

daily_job_downstream = BashOperator(
    bash_command="echo 1",
    task_id="daily_job_downstream",
    dag=dag,
)

daily_job = create_subdag_opt(main_dag=dag)

daily_job >> daily_job_downstream
