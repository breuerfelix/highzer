import json
from utils import pretty_time, pprint, locate_folder


def analyze_chat(ident, chunk_size):
    folder = locate_folder(ident)
    with open(f"{folder}/chat.json") as file:
        content = file.read()
        data = json.loads(content)

    print(f'VOD: {data["video"]["title"]}')

    output = []
    chunk_count = 0
    counter = 0

    for comment in sorted(data["comments"], key=lambda x: x["content_offset_seconds"]):
        offset = comment["content_offset_seconds"]
        msg = comment["message"]["body"]

        if msg.startswith("!"):
            # filter out commands
            continue

        if offset > (chunk_count + 1) * chunk_size:
            now = chunk_count * chunk_size
            output.append(
                {
                    "value": counter,
                    "chunk": chunk_count,
                    "pretty": pretty_time(chunk_count * chunk_size),
                    "from": now,
                    "length": chunk_size,
                    "to": now + chunk_size,
                }
            )

            # reset
            counter = 0
            chunk_count += 1

        counter += 1

    sort = sorted(output, reverse=True, key=lambda x: x["value"])
    sorted_top = sorted(sort[:10], key=lambda x: x["from"])
    pprint(sort[:10])

    return sort, sorted_top
