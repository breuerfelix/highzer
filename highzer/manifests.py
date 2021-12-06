import yaml
from slugify import slugify
from kubernetes import client, config, utils
from .config import UPLOAD_URL, PASSPHRASE
from .utils import locate_folder

IMAGE = "ghcr.io/breuerfelix/highzer:latest"
NAMESPACE = "highzer"

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

    data.append(gen_cleanup_job(NAMESPACE))
    data.append(gen_role(NAMESPACE, "highzer"))
    data.append(gen_role_binding(NAMESPACE, "highzer"))
    return yaml.dump_all(data)


def apply_merge_job(game, prefix, n):
    name = f"{prefix}-{slugify(game)}"
    res = {
        "requests": {
            "cpu": "2000m",
            "memory": "3000Mi",
        },
    }

    volumeMounts = [{
        "name": "meta-json",
        "mountPath": "/usr/app/data/static"
    }]

    volumes = [{
        "name": "meta-json",
        "configMap": {
            "name": name,
            "items": [{
                "key": "meta.json",
                "path": "meta.json",
            }],
        },
    }]


    job = gen_job(
        NAMESPACE,
        f"{name}-{n}",
        IMAGE,
        ["highzer", "merge", game],
        [
            {"name": "UPLOAD_URL", "value": UPLOAD_URL},
            {"name": "PASSPHRASE", "value": PASSPHRASE},
        ],
        res,
        volumeMounts,
        volumes,
    )

    folder = locate_folder("static")
    filename = f"{folder}/meta.json"
    with open(filename, "r") as f:
        raw = f.read()

    body = {
      "data": {
        "meta.json": raw,
      },
    }

    config.load_config()
    cm_client = client.CoreV1Api()
    cm_client.patch_namespaced_config_map(name, NAMESPACE, body)

    k8s_client = client.ApiClient()
    utils.create_from_dict(k8s_client, job)


def gen_prepare(name, schedule, command, upload_url, passphrase):
    cj = gen_cronjob(
        NAMESPACE,
        name,
        schedule,
        IMAGE,
        command,
        [
            {"name": "UPLOAD_URL", "value": upload_url},
            {"name": "PASSPHRASE", "value": passphrase},
        ],
    )

    cm = gen_configmap(NAMESPACE, name, {"meta.json": ""})

    return [cj, cm]


def gen_job(
    namespace,
    name,
    image,
    command,
    env = [],
    resources = {},
    volumeMounts = [],
    volumes = [],
    backoffLimit = 5,
):
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
                            "volumeMounts": volumeMounts,
                        },
                    ],
                    "volumes": volumes,
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


def gen_cleanup_job(namespace):
    return gen_cronjob(
        namespace,
        "cleanup-jobs",
        "*/30 * * * *",
        "wernight/kubectl",
        ["sh", "-c", "kubectl get jobs | awk '$4 ~ /[2-9]d$/ || $3 ~ 1' | awk '{print $1}' | xargs kubectl delete job"],
    )


def gen_role(namespace, name):
    return {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "Role",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "rules": [{
            "apiGroups": ["", "batch"],
            "resources": ["jobs", "configmaps"],
            "verbs": ["list", "create", "update", "patch", "delete"],
        }],
    }


def gen_role_binding(namespace, name):
    return {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "RoleBinding",
        "metadata": {
            "name": name,
            "namespace": namespace,
        },
        "roleRef": {
            "apiGroup": "rbac.authorization.k8s.io",
            "kind": "Role",
            "name": name,
        },
        "subjects": [{
            "kind": "ServiceAccount",
            "name": "default",
            "namespace": "highzer"
        }],
    }

