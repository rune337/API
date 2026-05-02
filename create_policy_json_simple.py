import csv
import json
from pathlib import Path


BUCKET_NAME = "bucket"

ALLOW_ACTIONS = [
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject",
]

KEEP_ACTIONS = [
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject",
    "s3:DeleteObjectVersion",
]


def build_bucket_arn():
    return f"arn:aws:s3:::{BUCKET_NAME}"


def split_folders(raw_value):
    if not raw_value:
        return []

    result = []
    for value in raw_value.split("|"):
        folder = value.strip()
        if folder:
            result.append(folder)

    return result


def build_object_arn(folder):
    return f"{build_bucket_arn()}/{folder}/*"


def build_keep_arn(folder):
    return f"{build_bucket_arn()}/{folder}/.keep"


def build_allow_bucket_statement():
    return {
        "Sid": "AllowBucket",
        "Effect": "Allow",
        "Action": "s3:ListBucket",
        "Resource": build_bucket_arn(),
    }


def build_allow_folder_statement(folder):
    return {
        "Sid": f"Allow{folder.replace('/', '_')}",
        "Effect": "Allow",
        "Action": ALLOW_ACTIONS,
        "Resource": build_object_arn(folder),
    }


def build_keep_statement(folder):
    return {
        "Sid": f"Keep{folder.replace('/', '_')}",
        "Effect": "Deny",
        "Action": KEEP_ACTIONS,
        "Resource": build_keep_arn(folder),
    }


def build_deny_bucket_statement(prefix):
    return {
        "Sid": f"DenyBucket{prefix.replace('/', '_').replace('*', 'All')}",
        "Effect": "Deny",
        "Action": "s3:ListBucket",
        "Resource": build_bucket_arn(),
        "Condition": {
            "StringLike": {
                "s3:prefix": prefix
            }
        },
    }


def build_deny_folder_statement(folder):
    return {
        "Sid": f"Deny{folder.replace('/', '_')}",
        "Effect": "Deny",
        "Action": ALLOW_ACTIONS,
        "Resource": build_object_arn(folder),
    }


def create_policy_if_needed(policies, policy_name):
    if policy_name not in policies:
        policies[policy_name] = {
            "Version": "2012-10-17",
            "Statement": [build_allow_bucket_statement()],
        }


def load_policies(input_csv):
    policies = {}

    with open(input_csv, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            policy_name = row["PolicyName"].strip()
            folders = split_folders(row["Folder"])
            exclude_prefix = row["ExcludePrefix"].strip()
            is_not_create = policy_name.lower() == "not create"

            if not policy_name or not folders:
                continue

            create_policy_if_needed(policies, policy_name)

            for folder in folders:
                policies[policy_name]["Statement"].append(
                    build_allow_folder_statement(folder)
                )
                policies[policy_name]["Statement"].append(
                    build_keep_statement(folder)
                )

                if is_not_create:
                    policies[policy_name]["Statement"].append(
                        build_deny_folder_statement(folder)
                    )

            if is_not_create and exclude_prefix:
                policies[policy_name]["Statement"].append(
                    build_deny_bucket_statement(exclude_prefix)
                )

    return policies


def write_policies(policies, output_dir):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for policy_name, policy_doc in policies.items():
        file_path = output_path / f"{policy_name}.json"
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(policy_doc, json_file, ensure_ascii=False, indent=2)


def main():
    input_csv = "policy_simple.csv"
    output_dir = "Json"
    policies = load_policies(input_csv)
    write_policies(policies, output_dir)
    print(f"{len(policies)} 件のポリシーJSONを {output_dir} に出力しました。")


if __name__ == "__main__":
    main()
