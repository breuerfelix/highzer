import yaml
from slugify import slugify
from .config import UPLOAD_URL, PASSPHRASE
from kubernetes import client, config, utils

IMAGE = "ghcr.io/breuerfelix/highzer:latest"

def generate_manifests(games, upload_url, passphrase):
    data = list()
    for game in games:
        g = slugify(game)
        data.extend(
            gen_prepare(
                f"daily-{g}",
                "0 22 * * *",
                ["highzer", "prepare-daily", game],
                upload_url,
                passphrase,
            )
        )

        data.extend(
            gen_prepare(
                f"weekly-{g}",
                "0 12 * * 6",
                ["highzer", "prepare-weekly", game],
                upload_url,
                passphrase,
            )
        )

    return yaml.dump_all(data)


def apply_merge_job(game, prefix):
    res = {
        "requests": {
            "cpu": "2000m",
            "memory": "3000Mi",
        },
    }

    job = gen_job(
        "highzer",
        f"{prefix}-{slugify(game)}",
        IMAGE,
        ["highzer", "merge", game],
        [
            {"name": "UPLOAD_URL", "value": UPLOAD_URL},
            {"name": "PASSPHRASE", "value": PASSPHRASE},
        ],
        res,
    )

    config.load_config()
    k8s_client = client.ApiClient()
    utils.create_from_dict(k8s_client, job)


def gen_prepare(name, schedule, command, upload_url, passphrase):
    ns = "highzer"
    cj = gen_cronjob(
        ns,
        name,
        schedule,
        IMAGE,
        command,
        [
            {"name": "UPLOAD_URL", "value": upload_url},
            {"name": "PASSPHRASE", "value": passphrase},
        ],
    )

    cm = gen_configmap(ns, name, {"meta.json": ""})
    return [cj, cm]


def gen_job(namespace, name, image, command, env = [], resources = {}, backoffLimit = 5):
    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "spec": {
            "template": {
                "spec": {
                    "restartPolicy": "Never",
                    "containers": [
                        {
                            "name": name,
                            "image": image,
                            "imagePullPolicy": "Always",
                            "command": command,
                            "env": env,
                            "resources": resources,
                            "volumeMounts": [{
                                "name": "meta-json",
                                "mountPath": "/usr/app/data/static"
                            }],
                        },
                    ],
                    "volumes": [{
                        "name": "meta-json",
                        "configMap": {
                            "name": name,
                            "items": [{
                                "key": "meta.json",
                                "path": "meta.json",
                            }],
                        },
                    }],
                },
            },
            "backoffLimit": backoffLimit,
        },
    }


def gen_cronjob(namespace, name, schedule, image, command, env = [], resources = {}):
    return {
        "apiVersion": "batch/v1",
        "kind": "CronJob",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "spec": {
            "schedule": schedule,
            "jobTemplate": {
                "spec": gen_job(namespace, name, image, command, env, resources)["spec"],
            },
        },
    }


def gen_configmap(namespace, name, data):
    return {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "data": data,
    }
