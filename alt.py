#!/usr/local/bin/python3
# -*- encoding: utf-8 -*-
#                 _  __ _       __                       __    _              #
#                | |/ /(_)___  / /_____  ____  ____ _   / /   (_)             #
#                |   // / __ \/ __/ __ \/ __ \/ __ `/  / /   / /              #
#               /   |/ / / / / /_/ /_/ / / / / /_/ /  / /___/ /               #
#              /_/|_/_/_/ /_/\__/\____/_/ /_/\__, /  /_____/_/                #
#                                           /____/                            #

import argparse
import curses
import linecache
import os
import unicodedata


def flen(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def chrWidth(c):
    if (unicodedata.east_asian_width(c) in ('F','W')):
        return 2
    else:
        return 1


def prtlen(s):
    return sum([chrWidth(c) for c in s])


def numberString(string):
    string_list = string.split()
    string_len = len(string_list)
    idx_list = [str(idx+1) for idx in range(string_len)]
    for i in range(string_len):
        if prtlen(string_list[i]) > len(idx_list[i]):
            idx_list[i] += ' ' * (prtlen(string_list[i]) - len(idx_list[i]))
        elif len(idx_list[i]) > prtlen(string_list[i]):
            string_list[i] += ' ' * (len(idx_list[i]) - prtlen(string_list[i]))
    return string_list, idx_list


def alignString(align, align_sure):
    alignstr_list = []
    for i in range(len(align)):
        for j in range(len(align[i])):
            alignstr_list.append('{}:{}/{}'.format(
                align[i][j],
                i+1,
                1 if align_sure[i][j] else 0))
    return alignstr_list


def alignList(alignstr, tgt_list_len):
    align = [[] for _ in range(tgt_list_len)]
    align_sure = [[] for _ in range(tgt_list_len)]
    if alignstr == '':
        return align, align_sure
    items = alignstr.split()
    for item in items:
        link, flag = item.split('/')
        src, tgt = link.split(':')
        align[int(tgt)-1].append(int(src))
        if flag == '1':
            align_sure[int(tgt)-1].append(1)
        else:
            align_sure[int(tgt)-1].append(0)
    return align, align_sure


def draw(stdscr, f_src, f_tgt, f_align, args):
    f_src_len = flen(f_src)
    f_tgt_len = flen(f_src)
    assert f_src_len == f_tgt_len

    f_line = 0
    alignstr_total = [''] * f_src_len
    if os.path.isfile(f_align):
        with open(f_align, 'r') as f:
            for i, l in enumerate(f):
                alignstr_total[i] = l.strip()
                if l.strip() == '' and f_line == 0:
                    f_line = i + 1
    if f_line == 0: f_line = 1

    stdscr.refresh()

    key = 0
    step = 10
    margin = 5
    tgt_y = 3
    src_y = 7
    message_y = 11
    statusbarstr_y = 13
    align_y = 16

    sure = True
    tgt_cur = 0
    tgt_cur_x = 0
    src_cur = 0
    src_cur_x = 0
    selected = ''

    title = 'ALIGN LABEL TOOL'
    stdscr.addstr(tgt_y, 0, 'TGT')
    stdscr.addstr(src_y, 0, 'SRC')
    stdscr.addstr(align_y, 0, 'ALN')
    message = ''

    src = linecache.getline(f_src, f_line)
    tgt = linecache.getline(f_tgt, f_line)

    tgt_list, tgt_idx_list = numberString(tgt)
    tgt, tgt_idx = ' '.join(tgt_list), ' '.join(tgt_idx_list)
    tgt_pmincol = 0
    tgt_len = prtlen(tgt)

    src_list, src_idx_list = numberString(src)
    src, src_idx = ' '.join(src_list), ' '.join(src_idx_list)
    src_pmincol = 0
    src_len = prtlen(src)

    alignstr = alignstr_total[f_line-1]
    align, align_sure = alignList(alignstr, len(tgt_list))
    align_sure[tgt_cur] = [w for _, w in sorted(zip(align[tgt_cur],
                           align_sure[tgt_cur]))]
    align[tgt_cur].sort()
    alignstr_list = alignString(align, align_sure)
    alignstr = ' '.join(alignstr_list)
    align_pmincol = 0

    while True:
        stdscr.refresh()
        height, width = stdscr.getmaxyx()
        win_width = width - margin
        src_max_move = max(src_len - win_width + margin - 1, 0)
        tgt_max_move = max(tgt_len - win_width + margin - 1, 0)
        align_max_move = max(len(alignstr) - win_width + margin - 1, 0)

        title_x = int((width // 2) - (len(title) // 2) - len(title) % 2)
        stdscr.addstr(0, title_x, title)
        stdscr.addstr(0, 0, ' '*title_x)
        stdscr.addstr(0, title_x+len(title), ' '*(width-title_x-len(title)))

        if win_width > tgt_len:
            tgt += ' ' * (win_width - tgt_len - margin + 1)
            tgt_idx += ' ' * (win_width - tgt_len - margin + 1)
            tgt_len = prtlen(tgt)
        tgt_pad = curses.newpad(3, tgt_len)
        tgt_pad.addstr(1, 0, tgt)
        tgt_pad.addstr(0, 0, tgt_idx)
        tgt_pad.addstr(1, tgt_cur_x, tgt_list[tgt_cur], curses.A_STANDOUT)
        tgt_pad.addstr(0, tgt_cur_x, tgt_idx_list[tgt_cur], curses.A_STANDOUT)
        tgt_pad.refresh(0, tgt_pmincol, tgt_y, margin, tgt_y+3, win_width)

        if win_width > src_len:
            src += ' ' * (win_width - src_len - margin + 1)
            src_idx += ' ' * (win_width - src_len - margin + 1)
            src_len = prtlen(src)
        src_pad = curses.newpad(3, src_len)
        src_pad.addstr(0, 0, src)
        src_pad.addstr(1, 0, src_idx)
        for j in range(len(align[tgt_cur])):
            w = align[tgt_cur][j] - 1
            w_x = prtlen(' '.join(src_list[:w]))
            if w_x != 0: w_x += 1
            src_pad.addstr(0, w_x, src_list[w], curses.A_STANDOUT)
            if align_sure[tgt_cur][j]:
                src_pad.addstr(1, w_x, src_idx_list[w], curses.A_STANDOUT)
        src_pad.refresh(0, src_pmincol, src_y, margin, src_y+3, win_width)

        align_pad = curses.newpad(2, max(1, len(alignstr)))
        align_pad.addstr(0, 0, alignstr)
        for j in range(len(align[tgt_cur])):
            w = sum([len(align[i]) for i in range(tgt_cur)]) + j
            w_x = len(' '.join(alignstr_list[:w]))
            if w_x != 0: w_x += 1
            align_pad.addstr(0, w_x, alignstr_list[w], curses.A_STANDOUT)
        align_pad.refresh(0, align_pmincol, align_y, margin,
                          align_y+2, win_width)
        if len(alignstr) < win_width:
            stdscr.addstr(align_y, margin+len(alignstr),
                ' ' * (width - len(alignstr) - margin - 1))

        message_x = int((width // 2) - (prtlen(message) // 2) - \
            prtlen(message) % 2)
        stdscr.addstr(message_y, message_x, message)
        stdscr.addstr(message_y, 0, ' '*message_x)
        stdscr.addstr(message_y, message_x+prtlen(message),
            ' '*(width-message_x-prtlen(message)))

        statusbarstr = '{} | {}/{} | {} | {}'.format(
            'VIEW' if args.view else 'EDIT',
            f_line,
            f_src_len,
            '  SURE  ' if sure else 'POSSIBLE',
            selected)
        stdscr.addstr(statusbarstr_y, 0, statusbarstr)
        stdscr.addstr(statusbarstr_y, len(statusbarstr),
            ' ' * (width - len(statusbarstr) - 1))

        key = stdscr.getkey()
        if key == 's':
            sure = not sure
        elif key == 'n':
            tgt_cur = min(tgt_cur+1, len(tgt_list)-1)
            tgt_cur_x = prtlen(' '.join(tgt_list[:tgt_cur]))
            if tgt_cur_x != 0: tgt_cur_x += 1
            tgt_pmincol = min(max(tgt_cur_x - width // 2 + \
                prtlen(tgt_list[tgt_cur]), 0), tgt_max_move)

            selected_align = min(
                sum([len(align[i]) for i in range(tgt_cur)]), \
                len(alignstr_list) - 1)
            selected_align_x = \
                len(' '.join(alignstr_list[:selected_align+1]))
            if selected_align_x != 0: selected_align_x += 1
            align_pmincol = min(max(selected_align_x - width // 2 + \
                len(alignstr_list[int(selected_align)]), 0),
                align_max_move)

            if align[tgt_cur]:
                src_cur = align[tgt_cur][0] - 1
                src_cur_x = prtlen(' '.join(src_list[:src_cur]))
                if src_cur_x != 0: src_cur_x += 1
                src_pmincol = min(max(src_cur_x - width // 2 + \
                    len(src_list[int(src_cur)]), 0),
                    src_max_move)
        elif key == 'p':
            tgt_cur = max(0, tgt_cur-1)
            tgt_cur_x = prtlen(' '.join(tgt_list[:tgt_cur]))
            if tgt_cur_x != 0: tgt_cur_x += 1
            tgt_pmincol = min(max(tgt_cur_x - width // 2 + \
                prtlen(tgt_list[tgt_cur]), 0), tgt_max_move)

            selected_align = min(
                sum([len(align[i]) for i in range(tgt_cur)]), \
                len(alignstr_list) - 1)
            selected_align_x = \
                len(' '.join(alignstr_list[:selected_align+1]))
            if selected_align_x != 0: selected_align_x += 1
            align_pmincol = min(max(selected_align_x - width // 2 + \
                len(alignstr_list[int(selected_align)]), 0),
                align_max_move)

            if align[tgt_cur]:
                src_cur = align[tgt_cur][0] - 1
                src_cur_x = prtlen(' '.join(src_list[:src_cur]))
                if src_cur_x != 0: src_cur_x += 1
                src_pmincol = min(max(src_cur_x - width // 2 + \
                    len(src_list[int(src_cur)]), 0),
                    src_max_move)
        elif key == 'w':
            src_pmincol = min(src_pmincol+step, src_max_move)
        elif key == 'b':
            src_pmincol = max(0, src_pmincol-step)
        elif key == 'd':
            align_pmincol = min(align_pmincol+step, align_max_move)
        elif key == 'a':
            align_pmincol = max(0, align_pmincol-step)
        elif key == 'q':
            alignstr_total[f_line-1] = alignstr
            break

        if len(key) == 1 and ord(key) >= ord('0') and ord(key) <= ord('9'):
            selected += key
            message = ''
        elif key == ' ':
            if selected == '':
                message = 'Please input the number of a source word'
            elif int(selected) < 1 or int(selected) > len(src_list):
                message = 'No source word is numbered as {}'.format(selected)
                selected = ''
            elif int(selected) in align[tgt_cur]:
                j = align[tgt_cur].index(int(selected))
                del align[tgt_cur][j]
                del align_sure[tgt_cur][j]

                alignstr_list = alignString(align, align_sure)
                alignstr = ' '.join(alignstr_list)
                selected_align = min(
                    sum([len(align[i]) for i in range(tgt_cur)]) + j + 1,
                    len(alignstr_list) - 1)
                selected_align_x = \
                    len(' '.join(alignstr_list[:selected_align]))
                if selected_align_x != 0: selected_align_x += 1
                align_max_move = max(len(alignstr) - win_width + margin - 1, 0)
                if len(alignstr_list) > 1:
                    align_pmincol = min(max(selected_align_x - width // 2 + \
                        len(alignstr_list[selected_align]), 0),
                        align_max_move)

                selected_x = prtlen(' '.join(src_list[:int(selected)+1]))
                if selected_x != 0: selected_x += 1
                src_pmincol = min(max(selected_x - width // 2 + \
                    prtlen(src_list[int(selected)-1]), 0), src_max_move)

                message = '{}: {} DELETED'.format(selected,
                    src_list[int(selected)-1])
                selected = ''
            else:
                align[tgt_cur].append(int(selected))
                align_sure[tgt_cur].append(True if sure else False)
                align_sure[tgt_cur] = [w for _, w in sorted(zip(align[tgt_cur],
                                       align_sure[tgt_cur]))]
                align[tgt_cur].sort()

                alignstr_list = alignString(align, align_sure)
                alignstr = ' '.join(alignstr_list)
                selected_align = min(
                    sum([len(align[i]) for i in range(tgt_cur)]) + \
                        align[tgt_cur].index(int(selected)),
                    len(alignstr_list) - 1)
                selected_align_x = \
                    len(' '.join(alignstr_list[:selected_align+1]))
                if selected_align_x != 0: selected_align_x += 1
                align_max_move = max(len(alignstr) - win_width + margin - 1, 0)
                align_pmincol = min(max(selected_align_x - width // 2 + \
                    len(alignstr_list[int(selected_align)]), 0),
                    align_max_move)

                selected_x = prtlen(' '.join(src_list[:int(selected)-1]))
                if selected_x != 0: selected_x += 1
                src_pmincol = min(max(selected_x - width // 2 + \
                    prtlen(src_list[int(selected)-1]), 0), src_max_move)

                message = '{}: {} ADDED {}'.format(selected,
                    src_list[int(selected)-1],
                    'for sure' if sure else 'possiblely')
                selected = ''
        elif key == 'L':
            if selected == '':
                message = 'Please input the number of sentences'
                continue
            elif int(selected) < 1 or int(selected) > f_src_len:
                message = 'No sentences at number {}'.format(selected)
                selected = ''
                continue
            f_line_tmp = f_line
            f_line = int(selected)
            src = linecache.getline(f_src, f_line)
            tgt = linecache.getline(f_tgt, f_line)
            if src == '' or tgt == '':
                f_line = f_line_tmp
                src = linecache.getline(f_src, f_line)
                tgt = linecache.getline(f_tgt, f_line)
                message = 'No more next sentences'
            else:
                alignstr_total[f_line_tmp-1] = alignstr
                message = 'Go to sentences at number {}'.format(f_line)

            tgt_list, tgt_idx_list = numberString(tgt)
            tgt, tgt_idx = ' '.join(tgt_list), ' '.join(tgt_idx_list)
            tgt_pmincol = 0
            tgt_len = prtlen(tgt)

            src_list, src_idx_list = numberString(src)
            src, src_idx = ' '.join(src_list), ' '.join(src_idx_list)
            src_pmincol = 0
            src_len = prtlen(src)

            sure = True
            tgt_cur = 0
            tgt_cur_x = 0
            src_cur = 0
            src_cur_x = 0
            selected = ''

            alignstr = alignstr_total[f_line-1]
            align, align_sure = alignList(alignstr, len(tgt_list))
            align_sure[tgt_cur] = [w for _, w in sorted(zip(align[tgt_cur],
                                   align_sure[tgt_cur]))]
            align[tgt_cur].sort()
            alignstr_list = alignString(align, align_sure)
            alignstr = ' '.join(alignstr_list)
            align_pmincol = 0
        elif key == '>':
            f_line += 1
            src = linecache.getline(f_src, f_line)
            tgt = linecache.getline(f_tgt, f_line)
            if src == '' or tgt == '':
                f_line -= 1
                src = linecache.getline(f_src, f_line)
                tgt = linecache.getline(f_tgt, f_line)
                message = 'No more next sentences'
            else:
                alignstr_total[f_line-2] = alignstr
                message = 'Next sentences'

            tgt_list, tgt_idx_list = numberString(tgt)
            tgt, tgt_idx = ' '.join(tgt_list), ' '.join(tgt_idx_list)
            tgt_pmincol = 0
            tgt_len = prtlen(tgt)

            src_list, src_idx_list = numberString(src)
            src, src_idx = ' '.join(src_list), ' '.join(src_idx_list)
            src_pmincol = 0
            src_len = prtlen(src)

            sure = True
            tgt_cur = 0
            tgt_cur_x = 0
            src_cur = 0
            src_cur_x = 0
            selected = ''

            alignstr = alignstr_total[f_line-1]
            align, align_sure = alignList(alignstr, len(tgt_list))
            align_sure[tgt_cur] = [w for _, w in sorted(zip(align[tgt_cur],
                                   align_sure[tgt_cur]))]
            align[tgt_cur].sort()
            alignstr_list = alignString(align, align_sure)
            alignstr = ' '.join(alignstr_list)
            align_pmincol = 0
        elif key == '<':
            f_line -= 1
            src = linecache.getline(f_src, f_line)
            tgt = linecache.getline(f_tgt, f_line)
            if src == '' or tgt == '':
                f_line += 1
                src = linecache.getline(f_src, f_line)
                tgt = linecache.getline(f_tgt, f_line)
                message = 'No more previous sentences'
            else:
                alignstr_total[f_line] = alignstr
                message = 'Previous sentences'

            tgt_list, tgt_idx_list = numberString(tgt)
            tgt, tgt_idx = ' '.join(tgt_list), ' '.join(tgt_idx_list)
            tgt_pmincol = 0
            tgt_len = prtlen(tgt)

            src_list, src_idx_list = numberString(src)
            src, src_idx = ' '.join(src_list), ' '.join(src_idx_list)
            src_pmincol = 0
            src_len = prtlen(src)

            sure = True
            tgt_cur = 0
            tgt_cur_x = 0
            src_cur = 0
            src_cur_x = 0
            selected = ''

            alignstr = alignstr_total[f_line-1]
            align, align_sure = alignList(alignstr, len(tgt_list))
            align_sure[tgt_cur] = [w for _, w in sorted(zip(align[tgt_cur],
                                   align_sure[tgt_cur]))]
            align[tgt_cur].sort()
            alignstr_list = alignString(align, align_sure)
            alignstr = ' '.join(alignstr_list)
            align_pmincol = 0
        else:
            message = ''
            selected = ''
    return alignstr_total

def main(args):
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    f_src = args.source
    f_tgt = args.target
    f_align = args.align
    alignstr_total = draw(stdscr, f_src, f_tgt, f_align, args)

    curses.echo()
    curses.nocbreak()
    stdscr.keypad(False)
    curses.endwin()

    if not args.view:
        print('Saving alignments to {}'.format(f_align))
        with open(f_align, 'w') as f:
            for item in alignstr_total:
                f.write('%s\n' % item)
        print('Done')
    else:
        print('Quit without saving')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('target')
    parser.add_argument('align')
    parser.add_argument('-v', '--view', help='view only', action='store_true')
    args = parser.parse_args()
    main(args)
