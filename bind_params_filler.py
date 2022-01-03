#!/usr/bin/env python3

import re
import argparse
import logging


r_query_start = re.compile(r'^\d{4}.*duration:.*ms.*bind')
r_params_line = re.compile(r'^\d{4}.*parameters: \$1 = ')
r_params_capture = re.compile(r"""(\$\d+ = '.*?',)""")  # this leaves out the last param, which needs special capture
r_param_num_from_param_pair = re.compile(r"""(\$\d+) = '.*?',""") # "$12 = 'ABASASDFASF'," -> $12
r_param_value_from_param_pair = re.compile(r"""\$\d+ = ('.*?'),""") # "$12 = 'ABASASDFASF'," -> ABASASDFASF


def params_string_to_pairs(params_line):
    """2021-12-21 17:00:32.071 UTC-61c20813.14e28-DETAIL:  parameters: $1 = '9', $2 = '2665986911814221'....$14 = '1001' >>> ['$]"""
    ret = []

    matches = r_params_capture.findall(params_line)
    if not matches:
        # 1 param only maybe
        i = params_line.find("parameters: $1 = ")
        return [('$1', params_line[i + len("parameters: $1 = "):])]
    else:
        # the last param is missing the comma, add it for unified processing
        last_found_match_idx = params_line.find(matches[-1])
        last_param = params_line[last_found_match_idx + len(matches[-1]) + 1:].strip('\n') + ","
        matches.append(last_param)

    for m in matches:
        p = r_param_num_from_param_pair.findall(m)
        v = r_param_value_from_param_pair.findall(m)
        if p and v:
            ret.append((p[0], v[0]))
        else:
            logging.warning('could not extract param pair. line: %s', params_line)

    return ret


def replace_params_line_into_sql(sql, params):
    param_pairs = params_string_to_pairs(params)
    # need to reverse not to replace $1 with $11, i.e. replace bigger numbers first
    param_pairs_sorted = sorted(param_pairs, reverse=True, key=lambda x: int(x[0][1:]))

    sql_new = sql

    for p, v in param_pairs_sorted:
        sql_new = sql_new.replace(p, v, 1)

    return sql_new


def main():
    """NB! Verified only with log_line_prefix = '%m-%c-'"""
    argp = argparse.ArgumentParser(description='Scans PostgreSQL logfiles and replaces query parameters placeholders with read bind values where possible and stores to a new $file.binded file')
    argp.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='More chat')
    argp.add_argument('-e', '--explain', dest='explain', action='store_true', help='Prepend all binded SQLs with EXPLAIN for instant execution')
    argp.add_argument('files', metavar='FILE', nargs='+', help='Log files in stderr / syslog format')

    args = argp.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG if args.verbose else logging.WARNING)

    for file in args.files:
        
        fp = open(file)
        file_new = file + '.binded'
        fpn = None  # create results file only on 1st bind

        logging.info('processing: %s', file)

        query_found = False
        sql = ''
        bind_count = 0
        explain_emitted = False

        line = fp.readline()

        while line:

            if not query_found and r_query_start.match(line):
                sql = line  # let's also include the timestamp + duration line
                query_found = True  # start "capture" cycle, collect next query lines till params list
                logging.debug('found a bindable query: %s', line)
            elif query_found and not r_params_line.match(line):
                # logging.debug('collecting one line of SQL: %s', line)
                if args.explain and not explain_emitted:
                    sql += 'EXPLAIN \n'
                    explain_emitted = True
                sql += line
            elif query_found and r_params_line.match(line):
                logging.debug('found parameters - binding: %s', line)
                if not fpn:
                    fpn = open(file_new, 'w')
                binded_sql = replace_params_line_into_sql(sql, line)
                fpn.write(binded_sql)
                query_found = False
                bind_count += 1
                explain_emitted = False

            line = fp.readline()

        logging.warning('binded %s SQLs. Outfile: %s', bind_count, file_new)

        fp.close()
        if fpn:
            fpn.close()

    logging.info('Done. %s files processed', len(args.files))


if __name__ == '__main__':
    main()
