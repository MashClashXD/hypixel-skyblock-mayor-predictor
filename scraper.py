import re
import csv

def main():
    # Read the Lua code from a txt file
    input_filename = "mayor_data.txt"
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            lua_code = f.read()
    except FileNotFoundError:
        print(f"Input file '{input_filename}' not found.")
        return

    print("Loaded Lua code, length:", len(lua_code))

    # Extract the elections block
    elections_block_m = re.search(r'elections\s*=\s*\{(.*)\}\s*$', lua_code, re.DOTALL | re.MULTILINE)
    if not elections_block_m:
        print("No elections block found.")
        return
    elections_block = elections_block_m.group(1)
    print("Elections block extracted, length:", len(elections_block))

    # Find all elections (robustly match nested braces for each election)
    elections = []
    for em in re.finditer(r'\[(\d+)\]\s*=\s*\{', elections_block):
        start = em.end()
        election_num = em.group(1)
        # Find the matching closing brace for this election
        brace_count = 1
        i = start
        while i < len(elections_block) and brace_count > 0:
            if elections_block[i] == '{':
                brace_count += 1
            elif elections_block[i] == '}':
                brace_count -= 1
            i += 1
        block = elections_block[start:i-1]

        print(f"\n--- Election {election_num} ---")
        print("Election block (truncated):", block[:200], "..." if len(block) > 200 else "")

        # Date
        date_m = re.search(r'date\s*=\s*"([^"]+)"', block)
        date = date_m.group(1) if date_m else ""
        print("Date found:", date)
        # Candidates
        # Improved parsing of candidates block to handle Lua table format with named keys and nested braces

        # Find the start of the candidates block
        candidates_start = block.find('candidates')
        if candidates_start == -1:
            print("No candidates block found for election", election_num)
            continue

        # Find the opening brace for the candidates table
        brace_start = block.find('{', candidates_start)
        if brace_start == -1:
            print("No opening brace for candidates block found for election", election_num)
            continue

        # Now, find the matching closing brace for the candidates table
        brace_count = 1
        i = brace_start + 1
        while i < len(block) and brace_count > 0:
            if block[i] == '{':
                brace_count += 1
            elif block[i] == '}':
                brace_count -= 1
            i += 1
        if brace_count != 0:
            print("Unmatched braces in candidates block for election", election_num)
            continue

        candidates_block = block[brace_start + 1 : i - 1]
        # Remove any trailing comma from the candidates block
        candidates_block = candidates_block.rstrip()
        if candidates_block.endswith(","):
            candidates_block = candidates_block[:-1]
        print("Candidates block (truncated):", candidates_block[:200], "..." if len(candidates_block) > 200 else "")

        # Parse params for all candidates (shared for this election)
        params = parse_params(candidates_block)

        candidate_names, candidate_perks = parse_candidates(candidates_block, params)
        print("Candidate names:", candidate_names)
        print("Candidate perks:", candidate_perks)
        # Mayor
        mayor_m = re.search(r'mayor\s*=\s*\{((?:.|\n)*?)\}(,|$)', block)
        if mayor_m:
            print("Mayor block:", mayor_m.group(1))
        mayor_name, mayor_perks = parse_mayor_or_minister(mayor_m.group(1)) if mayor_m else ("", [])
        print("Mayor name:", mayor_name)
        print("Mayor perks:", mayor_perks)
        # Minister
        # Always try to parse the minister block, even if not present or not Foxy
        # This regex matches both:
        #   minister = { ... }
        #   minister = { name = "Paul", perks = { ... } }
        # and is robust to newlines and whitespace.
        minister_m = re.search(
            r'minister\s*=\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}\s*(,|$)', block, re.DOTALL
        )
        if minister_m:
            print("Minister block:", minister_m.group(1))
            minister_name, minister_perks = parse_mayor_or_minister(minister_m.group(1))
            print("Minister name:", minister_name)
            print("Minister perks:", minister_perks)
        else:
            # Try to find a minister name even if the block is missing
            print("Minister block not found. Attempting to infer minister from block...")
            # Try to find a minister name in the block, even if not in a block
            minister_name = ""
            minister_perks = []
            # Try to find a line like minister = "NAME"
            minister_name_m = re.search(r'minister\s*=\s*"([^"]+)"', block)
            if minister_name_m:
                minister_name = minister_name_m.group(1)
                print("Minister name (string):", minister_name)
            else:
                print("Minister name not found as string.")
            # No perks if not a block
            print("Minister perks: []")
        elections.append({
            "election_number": election_num,
            "date": date,
            "candidates": candidate_names,
            "perks": candidate_perks,
            "mayor": mayor_name,
            "minister": minister_name
        })

    # Write to CSV
    if elections:
        print("\nWriting to elections.csv...")
        with open("elections.csv", "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["election_number", "date", "candidates", "perks", "mayor", "minister"])
            for e in elections:
                print(f"Writing row: election_number={e['election_number']}, date={e['date']}, candidates={e['candidates']}, perks={e['perks']}, mayor={e['mayor']}, minister={e['minister']}")
                # Only join non-empty perks for the perks column
                perks_joined = ""
                if e["perks"]:
                    # For each candidate's perks, join non-empty perks, then join non-empty candidate perks
                    candidate_perks_joined = [
                        ",".join([perk for perk in perks if perk]) for perks in e["perks"]
                    ]
                    # Now join only non-empty candidate perks
                    perks_joined = ",".join([cp for cp in candidate_perks_joined if cp])
                writer.writerow([
                    str(e["election_number"]),
                    str(e["date"]),
                    ",".join(e["candidates"]) if e["candidates"] else "",
                    perks_joined,
                    str(e["mayor"]),
                    str(e["minister"])
                ])
        print("Election data written to elections.csv")
    else:
        print("No election data found. CSV not written.")

def parse_perks(perks_str, params=None):
    # perks_str: {Perks.LuckOfTheSea,Perks.FishingFestival}
    # params: dict for the whole candidate, e.g. {"extra_event": "Sweet Tooth"}
    print("Parsing perks from string:", perks_str, "with params:", params)
    perks = []
    # Remove outer braces if present
    perks_body = perks_str.strip()
    if perks_body.startswith("{"):
        perks_body = perks_body[1:]
    if perks_body.endswith("}"):
        perks_body = perks_body[:-1]
    # Remove trailing comma if present (e.g. "Perks.LuckOfTheSea,Perks.FishingFestival,")
    perks_body = perks_body.rstrip()
    if perks_body.endswith(","):
        perks_body = perks_body[:-1]
    print("Perks body after removing braces and trailing comma:", perks_body)

    # If the string is empty after removing braces, return empty list
    if not perks_body.strip():
        print("Parsed perks: []")
        return []
    # Split by comma, handle empty
    for perk_item in [p.strip() for p in perks_body.split(",") if p.strip()]:
        # Should be like Perks.LuckOfTheSea or Perks.ExtraEvent
        m = re.match(r'Perks\.([A-Za-z0-9_]+)', perk_item)
        if m:
            perk = m.group(1)
            # Now, if this is Perks.ExtraEvent, check if params for the candidate has extra_event
            if perk == "ExtraEvent" and params and "extra_event" in params:
                event = params["extra_event"]
                # Replace all non-alphanumeric with underscores, then collapse multiple underscores
                event_clean = re.sub(r'\W+', '_', event).strip('_')
                perks.append(f"Perks.ExtraEvent{event_clean}")
            else:
                perks.append(f"Perks.{perk}")
        elif perk_item:  # fallback, just add as is if not empty
            perks.append(perk_item)
    print("Parsed perks:", perks)
    return perks

def parse_params(candidates_block):
    """
    Extracts the params block from the entire candidates block and returns a dict.
    Only parses the overall params for the candidates list, not per-candidate.
    Example:
        candidates_block = '''
            Marina = {perks={Perks.LuckOfTheSea,Perks.FishingFestival},votes=320482,order=1},
            Paul = {perks={Perks.EZPZ},votes=78195,order=2},
            params={extra_event="Sweet Tooth"}
        '''
        parse_params(candidates_block) -> {'extra_event': 'Sweet Tooth'}
    """
    print("Parsing params from candidates block (truncated):", candidates_block[:100], "..." if len(candidates_block) > 100 else "")
    params = {}
    # Find the params={...} block at the end (or anywhere) in the candidates block
    m = re.search(r'params\s*=\s*\{([^}]*)\}', candidates_block)
    if not m:
        print("No params block found.")
        return params
    params_body = m.group(1)
    # Find all key="value" pairs inside the params body
    for match in re.finditer(r'(\w+)\s*=\s*"([^"]+)"', params_body):
        params[match.group(1)] = match.group(2)
    print("Parsed params dict:", params)
    return params

def parse_candidates(candidates_block, params=None):
    # Returns (ordered_names, perks_list)
    # Match each candidate robustly, including params and order
    print("Parsing candidates from block (truncated):", candidates_block[:200], "..." if len(candidates_block) > 200 else "")
    # Remove any trailing comma from the candidates block before parsing
    candidates_block = candidates_block.rstrip()
    if candidates_block.endswith(","):
        candidates_block = candidates_block[:-1]
    candidate_pattern = re.compile(
        r'(\w+)\s*=\s*\{(.*?)\}(?:,|$)', re.DOTALL)
    candidates = []
    for m in candidate_pattern.finditer(candidates_block):
        name = m.group(1)
        if name == "params":
            print(f"Skipping candidate with name 'params'")
            continue
        body = m.group(2)
        print(f"Parsing candidate: {name}, body (truncated): {body[:100]}{'...' if len(body) > 100 else ''}")
        # perks
        # Use a more robust regex to match the perks block, including nested braces
        perks_start = body.find('perks')
        if perks_start != -1:
            perks_brace_start = body.find('{', perks_start)
            if perks_brace_start != -1:
                brace_count = 1
                j = perks_brace_start + 1
                while j < len(body) and brace_count > 0:
                    if body[j] == '{':
                        brace_count += 1
                    elif body[j] == '}':
                        brace_count -= 1
                    j += 1
                # Fix: include the last closing brace in perks_inner
                perks_inner = body[perks_brace_start : j]  # includes both opening and closing brace
                perks_str = perks_inner
            else:
                perks_inner = "{}"
                perks_str = "{}"
        else:
            perks_inner = "{}"
            perks_str = "{}"
        print(f"Candidate {name} perks_str:", perks_str)
        # order
        order_m = re.search(r'order\s*=\s*(\d+)', body)
        order = int(order_m.group(1)) if order_m else 9999
        print(f"Candidate {name} order:", order)
        # Use the shared params for all candidates
        perks = parse_perks(perks_str, params)
        print(f"Candidate {name} parsed perks:", perks)
        candidates.append((order, name, perks))
    # Sort by order
    candidates.sort()
    names = [c[1] for c in candidates]
    perks_list = [c[2] for c in candidates]
    print("Final candidate names:", names)
    print("Final candidate perks list:", perks_list)
    return names, perks_list

def parse_mayor_or_minister(block):
    # block: name = "Marina", perks = {Perks.LuckOfTheSea,Perks.FishingFestival}, params = {extra_event="Fishing Festival"}
    print("Parsing mayor/minister block:", block)
    name_m = re.search(r'name\s*=\s*"([^"]+)"', block)
    name = name_m.group(1) if name_m else ""
    print("Parsed name:", name)
    # Robustly extract the perks block, including nested braces
    perks_start = block.find('perks')
    if perks_start != -1:
        perks_brace_start = block.find('{', perks_start)
        if perks_brace_start != -1:
            brace_count = 1
            j = perks_brace_start + 1
            while j < len(block) and brace_count > 0:
                if block[j] == '{':
                    brace_count += 1
                elif block[j] == '}':
                    brace_count -= 1
                j += 1
            perks_inner = block[perks_brace_start + 1 : j - 1]
            # Remove trailing comma if present in perks_inner
            perks_inner = perks_inner.rstrip()
            if perks_inner.endswith(","):
                perks_inner = perks_inner[:-1]
            print("Perks inner:", perks_inner)
            perks_str = "{" + perks_inner + "}"
        else:
            perks_inner = ""
            perks_str = "{}"
    else:
        perks_inner = ""
        perks_str = "{}"
    print("Parsed perks_str:", perks_str)
    # Do not use params for mayor/minister, as params is for all candidates
    perks = parse_perks(perks_str, None)
    print("Parsed perks:", perks)
    return name, perks

if __name__ == "__main__":
    main()
