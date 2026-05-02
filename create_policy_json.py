import csv
import json
from pathlib import Path


def normalize_action(action):
    """S3 action名のよくある誤記を補正する。"""
    fixed = action.strip()
    replacements = {
        "Objject": "Object",
        "GetObjject": "GetObject",
        "PutObjject": "PutObject",
        "DeleteObjject": "DeleteObject",
    }
    for wrong, correct in replacements.items():
        fixed = fixed.replace(wrong, correct)
    return fixed


def normalize_arn(resource):
    """ARNのよくある誤記を補正する。"""
    fixed = resource.strip()
    if not fixed:
        return fixed
    fixed = fixed.replace("rn:aws", "arn:aws")
    fixed = fixed.replace("arn:aws:::s3:::", "arn:aws:s3:::")
    fixed = fixed.replace("arn:aws:::s3::", "arn:aws:s3:::")
    return fixed


def split_values(raw_value):
    """'|' 区切りを配列にし、空要素を除外する。"""
    if not raw_value:
        return []
    return [value.strip() for value in raw_value.split("|") if value.strip()]


def to_single_or_list(values):
    if len(values) == 1:
        return values[0]
    return values


def build_statement(row):
    sid = row["sid"].strip()
    effect = row["Effect"].strip()
    actions = [normalize_action(action) for action in split_values(row["Action"])]
    resources = [normalize_arn(resource) for resource in split_values(row["Resource"])]
    prefix = row["prefix"].strip()

    statement = {
        "Sid": sid,
        "Effect": effect,
        "Action": to_single_or_list(actions),
        "Resource": to_single_or_list(resources),
    }

    if prefix:
        statement["Condition"] = {
            "StringLike": {
                "s3:prefix": prefix
            }
        }

    return statement


def build_policies(input_csv):
    policies = {}

    with open(input_csv, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            policy_name = row["Policy"].strip()
            if not policy_name:
                continue

            statement = build_statement(row)
            if not statement["Sid"]:
                continue

            policies.setdefault(
                policy_name,
                {
                    "Version": "2012-10-17",
                    "Statement": [],
                },
            )
            policies[policy_name]["Statement"].append(statement)

    return policies


def write_policies(policies, output_dir):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for policy_name, policy_doc in policies.items():
        file_name = policy_name.replace(" ", "_") + ".json"
        file_path = output_path / file_name
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(policy_doc, json_file, ensure_ascii=False, indent=2)


def main():
    input_csv = "policy.csv"
    output_dir = "Json"
    policies = build_policies(input_csv)
    write_policies(policies, output_dir)
    print(f"{len(policies)} 件のポリシーJSONを {output_dir} に出力しました。")


if __name__ == "__main__":
    main()
