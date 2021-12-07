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

    data.append(gen_role(NAMESPACE, NAMESPACE))
    data.append(gen_role_binding(NAMESPACE, NAMESPACE))

    return yaml.dump_all(data)


def apply_merge_job(game, prefix, n):
    current_name = f"{prefix}-{slugify(game)}"
    name = f"{current_name}-{n}"

    owner_ref = []

    config.load_config()
    b_client = client.BatchV1Api()

    jobs = b_client.list_namespaced_job(NAMESPACE)
    for job in jobs.items:
        if not current_name in job.metadata.name:
            continue

        if job.status.active == None:
            continue

        owner_ref.append({
            "apiVersion": "batch/v1",
            "kind": "Job",
            "name": job.metadata.name,
            "uid":  job.metadata.uid,
        })

    res = {
        "requests": {
            "cpu": "2000m",
            "memory": "3000Mi",
        },
    }

    volumeMounts = [{
        "name": "meta-json",
        "mountPath": "/usr/app/data/config",
    }]

    volumes = [{
        "name": "meta-json",
        "configMap": {
            "name": name,
        },
    }]


    job = gen_job(
        NAMESPACE,
        name,
        IMAGE,
        ["highzer", "merge", game],
        [
            {"name": "UPLOAD_URL", "value": UPLOAD_URL},
            {"name": "PASSPHRASE", "value": PASSPHRASE},
        ],
        res,
        volumeMounts,
        volumes,
        owner_ref,
    )

    folder = locate_folder("static")
    filename = f"{folder}/meta.json"
    with open(filename, "r") as f:
        raw = f.read()

    cm = gen_configmap(NAMESPACE, name, {"meta.json": raw}, owner_ref)

    data = [cm, job]

    k8s_client = client.ApiClient()
    utils.create_from_yaml(k8s_client, yaml_objects=data)


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

    return [cj]


def gen_job(
    namespace,
    name,
    image,
    command,
    env = [],
    resources = {},
    volumeMounts = [],
    volumes = [],
    owner_references = [],
    backoffLimit = 5,
):
    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "ownerReferences": owner_references,
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


def gen_configmap(namespace, name, data, owner_references = []):
    return {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "ownerReferences": owner_references,
        },
        "data": data,
    }


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
            "verbs": ["*"],
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

