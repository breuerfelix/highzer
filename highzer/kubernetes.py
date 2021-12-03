import yaml
from slugify import slugify

def generate_manifests(games, upload_url, passphrase):
    data = list()
    for game in games:
        g = slugify(game)
        data.append(gen_highzer(
            f"{g}-daily",
            "0 22 * * *",
            ["highzer", "daily", game],
            upload_url,
            passphrase,
        ))

        data.append(gen_highzer(
            f"{g}-weekly",
            "0 12 * * 6",
            ["highzer", "weekly", game],
            upload_url,
            passphrase,
        ))

    return yaml.dump_all(data)


def gen_highzer(name, schedule, command, upload_url, passphrase):
    return gen_cronjob(
        "default",
        name,
        schedule,
        "ghcr.io/breuerfelix/highzer:latest",
        command,
        [
            {"name": "UPLOAD_URL", "value": upload_url},
            {"name": "PASSPHRASE", "value": passphrase},
        ],
    )


def gen_cronjob(namespace, name, schedule, image, command, env):
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
                                },
                            ],
                        },
                    },
                },
            },
        },
    }
