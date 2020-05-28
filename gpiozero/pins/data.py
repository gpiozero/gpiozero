# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
# Copyright (c) 2018-2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2016-2019 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import os
import sys
from textwrap import dedent
from itertools import cycle
from operator import attrgetter
from collections import namedtuple

from ..exc import PinUnknownPi, PinMultiplePins, PinNoPins, PinInvalidPin
from ..devices import Device


# Some useful constants for describing pins

V1_8   = '1V8'
V3_3   = '3V3'
V5     = '5V'
GND    = 'GND'
NC     = 'NC' # not connected
GPIO0  = 'GPIO0'
GPIO1  = 'GPIO1'
GPIO2  = 'GPIO2'
GPIO3  = 'GPIO3'
GPIO4  = 'GPIO4'
GPIO5  = 'GPIO5'
GPIO6  = 'GPIO6'
GPIO7  = 'GPIO7'
GPIO8  = 'GPIO8'
GPIO9  = 'GPIO9'
GPIO10 = 'GPIO10'
GPIO11 = 'GPIO11'
GPIO12 = 'GPIO12'
GPIO13 = 'GPIO13'
GPIO14 = 'GPIO14'
GPIO15 = 'GPIO15'
GPIO16 = 'GPIO16'
GPIO17 = 'GPIO17'
GPIO18 = 'GPIO18'
GPIO19 = 'GPIO19'
GPIO20 = 'GPIO20'
GPIO21 = 'GPIO21'
GPIO22 = 'GPIO22'
GPIO23 = 'GPIO23'
GPIO24 = 'GPIO24'
GPIO25 = 'GPIO25'
GPIO26 = 'GPIO26'
GPIO27 = 'GPIO27'
GPIO28 = 'GPIO28'
GPIO29 = 'GPIO29'
GPIO30 = 'GPIO30'
GPIO31 = 'GPIO31'
GPIO32 = 'GPIO32'
GPIO33 = 'GPIO33'
GPIO34 = 'GPIO34'
GPIO35 = 'GPIO35'
GPIO36 = 'GPIO36'
GPIO37 = 'GPIO37'
GPIO38 = 'GPIO38'
GPIO39 = 'GPIO39'
GPIO40 = 'GPIO40'
GPIO41 = 'GPIO41'
GPIO42 = 'GPIO42'
GPIO43 = 'GPIO43'
GPIO44 = 'GPIO44'
GPIO45 = 'GPIO45'

# Board layout ASCII art

REV1_BOARD = """\
{style:white on green}+------------------{style:black on white}| |{style:white on green}--{style:on cyan}| |{style:on green}------+{style:reset}
{style:white on green}| {P1:{style} col2}{style:white on green} P1 {style:black on yellow}|C|{style:white on green}  {style:on cyan}|A|{style:on green}      |{style:reset}
{style:white on green}| {P1:{style} col1}{style:white on green}    {style:black on yellow}+-+{style:white on green}  {style:on cyan}+-+{style:on green}      |{style:reset}
{style:white on green}|                                |{style:reset}
{style:white on green}|                {style:on black}+---+{style:on green}          {style:black on white}+===={style:reset}
{style:white on green}|                {style:on black}|SoC|{style:on green}          {style:black on white}| USB{style:reset}
{style:white on green}|   {style:on black}|D|{style:on green} {style:bold}Pi Model{style:normal} {style:on black}+---+{style:on green}          {style:black on white}+===={style:reset}
{style:white on green}|   {style:on black}|S|{style:on green} {style:bold}{model:3s}V{pcb_revision:3s}{style:normal}                  |{style:reset}
{style:white on green}|   {style:on black}|I|{style:on green}                  {style:on black}|C|{style:black on white}+======{style:reset}
{style:white on green}|                        {style:on black}|S|{style:black on white}|   Net{style:reset}
{style:white on green}|                        {style:on black}|I|{style:black on white}+======{style:reset}
{style:black on white}=pwr{style:on green}             {style:on white}|HDMI|{style:white on green}          |{style:reset}
{style:white on green}+----------------{style:black on white}|    |{style:white on green}----------+{style:reset}"""

REV2_BOARD = """\
{style:white on green}+------------------{style:black on white}| |{style:white on green}--{style:on cyan}| |{style:on green}------+{style:reset}
{style:white on green}| {P1:{style} col2}{style:white on green} P1 {style:black on yellow}|C|{style:white on green}  {style:on cyan}|A|{style:on green}      |{style:reset}
{style:white on green}| {P1:{style} col1}{style:white on green}    {style:black on yellow}+-+{style:white on green}  {style:on cyan}+-+{style:on green}      |{style:reset}
{style:white on green}|    {P5:{style} col1}{style:white on green}                        |{style:reset}
{style:white on green}| P5 {P5:{style} col2}{style:white on green}        {style:on black}+---+{style:on green}          {style:black on white}+===={style:reset}
{style:white on green}|                {style:on black}|SoC|{style:on green}          {style:black on white}| USB{style:reset}
{style:white on green}|   {style:on black}|D|{style:on green} {style:bold}Pi Model{style:normal} {style:on black}+---+{style:on green}          {style:black on white}+===={style:reset}
{style:white on green}|   {style:on black}|S|{style:on green} {style:bold}{model:3s}V{pcb_revision:3s}{style:normal}                  |{style:reset}
{style:white on green}|   {style:on black}|I|{style:on green}                  {style:on black}|C|{style:black on white}+======{style:reset}
{style:white on green}|                        {style:on black}|S|{style:black on white}|   Net{style:reset}
{style:white on green}|                        {style:on black}|I|{style:black on white}+======{style:reset}
{style:black on white}=pwr{style:on green}             {style:on white}|HDMI|{style:white on green}          |{style:reset}
{style:white on green}+----------------{style:black on white}|    |{style:white on green}----------+{style:reset}"""

A_BOARD = """\
{style:white on green}+------------------{style:black on white}| |{style:white on green}--{style:on cyan}| |{style:on green}------+{style:reset}
{style:white on green}| {P1:{style} col2}{style:white on green} P1 {style:black on yellow}|C|{style:white on green}  {style:on cyan}|A|{style:on green}      |{style:reset}
{style:white on green}| {P1:{style} col1}{style:white on green}    {style:black on yellow}+-+{style:white on green}  {style:on cyan}+-+{style:on green}      |{style:reset}
{style:white on green}|    {P5:{style} col1}{style:white on green}                        |{style:reset}
{style:white on green}| P5 {P5:{style} col2}{style:white on green}        {style:on black}+---+{style:on green}          {style:black on white}+===={style:reset}
{style:white on green}|                {style:on black}|SoC|{style:on green}          {style:black on white}| USB{style:reset}
{style:white on green}|   {style:on black}|D|{style:on green} {style:bold}Pi Model{style:normal} {style:on black}+---+{style:on green}          {style:black on white}+===={style:reset}
{style:white on green}|   {style:on black}|S|{style:on green} {style:bold}{model:3s}V{pcb_revision:3s}{style:normal}                  |{style:reset}
{style:white on green}|   {style:on black}|I|{style:on green}                  {style:on black}|C|{style:on green}     |{style:reset}
{style:white on green}|                        {style:on black}|S|{style:on green}     |{style:reset}
{style:white on green}|                        {style:on black}|I|{style:on green}     |{style:reset}
{style:black on white}=pwr{style:on green}             {style:on white}|HDMI|{style:white on green}          |{style:reset}
{style:white on green}+----------------{style:black on white}|    |{style:white on green}----------+{style:reset}"""

BPLUS_BOARD = """\
{style:white on green},--------------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8     {style:black on white}+===={style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}        {style:black on white}| USB{style:reset}
{style:white on green}|                             {style:black on white}+===={style:reset}
{style:white on green}|      {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal}         |{style:reset}
{style:white on green}|      {style:on black}+----+{style:on green}                 {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|D|{style:on green}  {style:on black}|SoC |{style:on green}                 {style:black on white}| USB{style:reset}
{style:white on green}| {style:on black}|S|{style:on green}  {style:on black}|    |{style:on green}                 {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|I|{style:on green}  {style:on black}+----+{style:on green}                    |{style:reset}
{style:white on green}|                   {style:on black}|C|{style:on green}     {style:black on white}+======{style:reset}
{style:white on green}|                   {style:on black}|S|{style:on green}     {style:black on white}|   Net{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}        {style:black on white}|HDMI|{style:white on green} {style:on black}|I||A|{style:on green}  {style:black on white}+======{style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}--------{style:black on white}|    |{style:white on green}----{style:on black}|V|{style:on green}-------'{style:reset}"""

B3PLUS_BOARD = """\
{style:white on green},--------------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8     {style:black on white}+===={style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}  PoE   {style:black on white}| USB{style:reset}
{style:white on green}| {style:black on white} Wi {style:white on green}                   {style:white on black}oo{style:on green}   {style:black on white}+===={style:reset}
{style:white on green}| {style:black on white} Fi {style:white on green} {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal} {style:white on black}oo{style:on green}      |{style:reset}
{style:white on green}|        {style:black on white},----.{style:on green}               {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|D|{style:on green}    {style:black on white}|SoC |{style:on green}               {style:black on white}| USB{style:reset}
{style:white on green}| {style:on black}|S|{style:on green}    {style:black on white}|    |{style:on green}               {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|I|{style:on green}    {style:black on white}`----'{style:white on green}                  |{style:reset}
{style:white on green}|                   {style:on black}|C|{style:on green}     {style:black on white}+======{style:reset}
{style:white on green}|                   {style:on black}|S|{style:on green}     {style:black on white}|   Net{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}        {style:black on white}|HDMI|{style:white on green} {style:on black}|I||A|{style:on green}  {style:black on white}+======{style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}--------{style:black on white}|    |{style:white on green}----{style:on black}|V|{style:on green}-------'{style:reset}"""

B4_BOARD = """\
{style:white on green},--------------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8   {style:black on white}+======{style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}  PoE {style:black on white}|   Net{style:reset}
{style:white on green}| {style:black on white} Wi {style:white on green}                   {style:white on black}oo{style:on green} {style:black on white}+======{style:reset}
{style:white on green}| {style:black on white} Fi {style:white on green} {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal} {style:white on black}oo{style:on green}      |{style:reset}
{style:white on green}|        {style:black on white},----.{style:on green}               {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|D|{style:on green}    {style:black on white}|SoC |{style:on green}               {style:black on white}|USB3{style:reset}
{style:white on green}| {style:on black}|S|{style:on green}    {style:black on white}|    |{style:on green}               {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|I|{style:on green}    {style:black on white}`----'{style:white on green}                  |{style:reset}
{style:white on green}|                   {style:on black}|C|{style:on green}       {style:black on white}+===={style:reset}
{style:white on green}|                   {style:on black}|S|{style:on green}       {style:black on white}|USB2{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}   {style:black on white}|HD|{style:white on green}   {style:black on white}|HD|{style:white on green} {style:on black}|I||A|{style:on green}    {style:black on white}+===={style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}---{style:black on white}|MI|{style:white on green}---{style:black on white}|MI|{style:white on green}----{style:on black}|V|{style:on green}-------'{style:reset}"""

APLUS_BOARD = """\
{style:white on green},--------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8  |{style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}     |{style:reset}
{style:white on green}|                          |{style:reset}
{style:white on green}|      {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal}   |{style:reset}
{style:white on green}|      {style:on black}+----+{style:on green}           {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|D|{style:on green}  {style:on black}|SoC |{style:on green}           {style:black on white}| USB{style:reset}
{style:white on green}| {style:on black}|S|{style:on green}  {style:on black}|    |{style:on green}           {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|I|{style:on green}  {style:on black}+----+{style:on green}              |{style:reset}
{style:white on green}|                   {style:on black}|C|{style:on green}    |{style:reset}
{style:white on green}|                   {style:on black}|S|{style:on green}    |{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}        {style:black on white}|HDMI|{style:white on green} {style:on black}|I||A|{style:on green} |{style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}--------{style:black on white}|    |{style:white on green}----{style:on black}|V|{style:on green}-'{style:reset}"""

A3PLUS_BOARD = """\
{style:white on green},--------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8  |{style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}     |{style:reset}
{style:white on green}| {style:black on white} Wi {style:white on green}                     |{style:reset}
{style:white on green}| {style:black on white} Fi {style:white on green} {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal}   |{style:reset}
{style:white on green}|        {style:black on white},----.{style:on green}         {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|D|{style:on green}    {style:black on white}|SoC |{style:on green}         {style:black on white}| USB{style:reset}
{style:white on green}| {style:on black}|S|{style:on green}    {style:black on white}|    |{style:on green}         {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|I|{style:on green}    {style:black on white}`----'{style:white on green}            |{style:reset}
{style:white on green}|                   {style:on black}|C|{style:on green}    |{style:reset}
{style:white on green}|                   {style:on black}|S|{style:on green}    |{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}        {style:black on white}|HDMI|{style:white on green} {style:on black}|I||A|{style:on green} |{style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}--------{style:black on white}|    |{style:white on green}----{style:on black}|V|{style:on green}-'{style:reset}"""

ZERO12_BOARD = """\
{style:white on green},-------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8 |{style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}    |{style:reset}
{style:black on white}---+{style:white on green}       {style:on black}+---+{style:on green}  {style:bold}PiZero{style:normal}  |{style:reset}
{style:black on white} sd|{style:white on green}       {style:on black}|SoC|{style:on green}   {style:bold}V{pcb_revision:3s}{style:normal}   |{style:reset}
{style:black on white}---+|hdmi|{style:white on green} {style:on black}+---+{style:on green}  {style:black on white}usb{style:on green} {style:black on white}pwr{style:white on green} |{style:reset}
{style:white on green}`---{style:black on white}|    |{style:white on green}--------{style:black on white}| |{style:white on green}-{style:black on white}| |{style:white on green}-'{style:reset}"""

ZERO13_BOARD = """\
{style:white on green}.-------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8 |{style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}   {style:black on white}|c{style:reset}
{style:black on white}---+{style:white on green}       {style:on black}+---+{style:on green} {style:bold}Pi{model:6s}{style:normal}{style:black on white}|s{style:reset}
{style:black on white} sd|{style:white on green}       {style:on black}|SoC|{style:on green}   {style:bold}V{pcb_revision:3s}{style:normal}  {style:black on white}|i{style:reset}
{style:black on white}---+|hdmi|{style:white on green} {style:on black}+---+{style:on green}  {style:black on white}usb{style:on green} {style:on white}pwr{style:white on green} |{style:reset}
{style:white on green}`---{style:black on white}|    |{style:white on green}--------{style:black on white}| |{style:white on green}-{style:black on white}| |{style:white on green}-'{style:reset}"""

CM_BOARD = """\
{style:white on green}+---------------------------------------+{style:reset}
{style:white on green}| {style:yellow on black}O{style:bold white on green}  Raspberry Pi {model:4s}                {style:normal yellow on black}O{style:white on green} |{style:reset}
 {style:white on green})   Version {pcb_revision:3s}     {style:on black}+---+{style:on green}             ({style:reset}
{style:white on green}|                    {style:on black}|SoC|{style:on green}              |{style:reset}
 {style:white on green})                   {style:on black}+---+{style:on green}             ({style:reset}
{style:white on green}| {style:on black}O{style:on green}   _                               {style:on black}O{style:on green} |{style:reset}
{style:white on green}||||||{style:reset} {style:white on green}||||||||||||||||||||||||||||||||||{style:reset}
"""

# Pin maps for various board revisions and headers

REV1_P1 = {
#   pin  func  pullup  pin  func  pullup
    1:  (V3_3,   False), 2:  (V5,     False),
    3:  (GPIO0,  True),  4:  (V5,     False),
    5:  (GPIO1,  True),  6:  (GND,    False),
    7:  (GPIO4,  False), 8:  (GPIO14, False),
    9:  (GND,    False), 10: (GPIO15, False),
    11: (GPIO17, False), 12: (GPIO18, False),
    13: (GPIO21, False), 14: (GND,    False),
    15: (GPIO22, False), 16: (GPIO23, False),
    17: (V3_3,   False), 18: (GPIO24, False),
    19: (GPIO10, False), 20: (GND,    False),
    21: (GPIO9,  False), 22: (GPIO25, False),
    23: (GPIO11, False), 24: (GPIO8,  False),
    25: (GND,    False), 26: (GPIO7,  False),
    }

REV2_P1 = {
    1:  (V3_3,   False), 2:  (V5,     False),
    3:  (GPIO2,  True),  4:  (V5,     False),
    5:  (GPIO3,  True),  6:  (GND,    False),
    7:  (GPIO4,  False), 8:  (GPIO14, False),
    9:  (GND,    False), 10: (GPIO15, False),
    11: (GPIO17, False), 12: (GPIO18, False),
    13: (GPIO27, False), 14: (GND,    False),
    15: (GPIO22, False), 16: (GPIO23, False),
    17: (V3_3,   False), 18: (GPIO24, False),
    19: (GPIO10, False), 20: (GND,    False),
    21: (GPIO9,  False), 22: (GPIO25, False),
    23: (GPIO11, False), 24: (GPIO8,  False),
    25: (GND,    False), 26: (GPIO7,  False),
    }

REV2_P5 = {
    1:  (V5,     False), 2:  (V3_3,   False),
    3:  (GPIO28, False), 4:  (GPIO29, False),
    5:  (GPIO30, False), 6:  (GPIO31, False),
    7:  (GND,    False), 8:  (GND,    False),
    }

PLUS_J8 = {
    1:  (V3_3,   False), 2:  (V5,     False),
    3:  (GPIO2,  True),  4:  (V5,     False),
    5:  (GPIO3,  True),  6:  (GND,    False),
    7:  (GPIO4,  False), 8:  (GPIO14, False),
    9:  (GND,    False), 10: (GPIO15, False),
    11: (GPIO17, False), 12: (GPIO18, False),
    13: (GPIO27, False), 14: (GND,    False),
    15: (GPIO22, False), 16: (GPIO23, False),
    17: (V3_3,   False), 18: (GPIO24, False),
    19: (GPIO10, False), 20: (GND,    False),
    21: (GPIO9,  False), 22: (GPIO25, False),
    23: (GPIO11, False), 24: (GPIO8,  False),
    25: (GND,    False), 26: (GPIO7,  False),
    27: (GPIO0,  False), 28: (GPIO1,  False),
    29: (GPIO5,  False), 30: (GND,    False),
    31: (GPIO6,  False), 32: (GPIO12, False),
    33: (GPIO13, False), 34: (GND,    False),
    35: (GPIO19, False), 36: (GPIO16, False),
    37: (GPIO26, False), 38: (GPIO20, False),
    39: (GND,    False), 40: (GPIO21, False),
    }

CM_SODIMM = {
    1:   (GND,              False), 2:   ('EMMC DISABLE N', False),
    3:   (GPIO0,            False), 4:   (NC,               False),
    5:   (GPIO1,            False), 6:   (NC,               False),
    7:   (GND,              False), 8:   (NC,               False),
    9:   (GPIO2,            False), 10:  (NC,               False),
    11:  (GPIO3,            False), 12:  (NC,               False),
    13:  (GND,              False), 14:  (NC,               False),
    15:  (GPIO4,            False), 16:  (NC,               False),
    17:  (GPIO5,            False), 18:  (NC,               False),
    19:  (GND,              False), 20:  (NC,               False),
    21:  (GPIO6,            False), 22:  (NC,               False),
    23:  (GPIO7,            False), 24:  (NC,               False),
    25:  (GND,              False), 26:  (GND,              False),
    27:  (GPIO8,            False), 28:  (GPIO28,           False),
    29:  (GPIO9,            False), 30:  (GPIO29,           False),
    31:  (GND,              False), 32:  (GND,              False),
    33:  (GPIO10,           False), 34:  (GPIO30,           False),
    35:  (GPIO11,           False), 36:  (GPIO31,           False),
    37:  (GND,              False), 38:  (GND,              False),
    39:  ('GPIO0-27 VREF',  False), 40:  ('GPIO0-27 VREF',  False),
    # Gap in SODIMM pins
    41:  ('GPIO28-45 VREF', False), 42:  ('GPIO28-45 VREF', False),
    43:  (GND,              False), 44:  (GND,              False),
    45:  (GPIO12,           False), 46:  (GPIO32,           False),
    47:  (GPIO13,           False), 48:  (GPIO33,           False),
    49:  (GND,              False), 50:  (GND,              False),
    51:  (GPIO14,           False), 52:  (GPIO34,           False),
    53:  (GPIO15,           False), 54:  (GPIO35,           False),
    55:  (GND,              False), 56:  (GND,              False),
    57:  (GPIO16,           False), 58:  (GPIO36,           False),
    59:  (GPIO17,           False), 60:  (GPIO37,           False),
    61:  (GND,              False), 62:  (GND,              False),
    63:  (GPIO18,           False), 64:  (GPIO38,           False),
    65:  (GPIO19,           False), 66:  (GPIO39,           False),
    67:  (GND,              False), 68:  (GND,              False),
    69:  (GPIO20,           False), 70:  (GPIO40,           False),
    71:  (GPIO21,           False), 72:  (GPIO41,           False),
    73:  (GND,              False), 74:  (GND,              False),
    75:  (GPIO22,           False), 76:  (GPIO42,           False),
    77:  (GPIO23,           False), 78:  (GPIO43,           False),
    79:  (GND,              False), 80:  (GND,              False),
    81:  (GPIO24,           False), 82:  (GPIO44,           False),
    83:  (GPIO25,           False), 84:  (GPIO45,           False),
    85:  (GND,              False), 86:  (GND,              False),
    87:  (GPIO26,           False), 88:  ('GPIO46 1V8',     False),
    89:  (GPIO27,           False), 90:  ('GPIO47 1V8',     False),
    91:  (GND,              False), 92:  (GND,              False),
    93:  ('DSI0 DN1',       False), 94:  ('DSI1 DP0',       False),
    95:  ('DSI0 DP1',       False), 96:  ('DSI1 DN0',       False),
    97:  (GND,              False), 98:  (GND,              False),
    99:  ('DSI0 DN0',       False), 100: ('DSI1 CP',        False),
    101: ('DSI0 DP0',       False), 102: ('DSI1 CN',        False),
    103: (GND,              False), 104: (GND,              False),
    105: ('DSI0 CN',        False), 106: ('DSI1 DP3',       False),
    107: ('DSI0 CP',        False), 108: ('DSI1 DN3',       False),
    109: (GND,              False), 110: (GND,              False),
    111: ('HDMI CK N',      False), 112: ('DSI1 DP2',       False),
    113: ('HDMI CK P',      False), 114: ('DSI1 DN2',       False),
    115: (GND,              False), 116: (GND,              False),
    117: ('HDMI D0 N',      False), 118: ('DSI1 DP1',       False),
    119: ('HDMI D0 P',      False), 120: ('DSI1 DN1',       False),
    121: (GND,              False), 122: (GND,              False),
    123: ('HDMI D1 N',      False), 124: (NC,               False),
    125: ('HDMI D1 P',      False), 126: (NC,               False),
    127: (GND,              False), 128: (NC,               False),
    129: ('HDMI D2 N',      False), 130: (NC,               False),
    131: ('HDMI D2 P',      False), 132: (NC,               False),
    133: (GND,              False), 134: (GND,              False),
    135: ('CAM1 DP3',       False), 136: ('CAM0 DP0',       False),
    137: ('CAM1 DN3',       False), 138: ('CAM0 DN0',       False),
    139: (GND,              False), 140: (GND,              False),
    141: ('CAM1 DP2',       False), 142: ('CAM0 CP',        False),
    143: ('CAM1 DN2',       False), 144: ('CAM0 CN',        False),
    145: (GND,              False), 146: (GND,              False),
    147: ('CAM1 CP',        False), 148: ('CAM0 DP1',       False),
    149: ('CAM1 CN',        False), 150: ('CAM0 DN1',       False),
    151: (GND,              False), 152: (GND,              False),
    153: ('CAM1 DP1',       False), 154: (NC,               False),
    155: ('CAM1 DN1',       False), 156: (NC,               False),
    157: (GND,              False), 158: (NC,               False),
    159: ('CAM1 DP0',       False), 160: (NC,               False),
    161: ('CAM1 DN0',       False), 162: (NC,               False),
    163: (GND,              False), 164: (GND,              False),
    165: ('USB DP',         False), 166: ('TVDAC',          False),
    167: ('USB DM',         False), 168: ('USB OTGID',      False),
    169: (GND,              False), 170: (GND,              False),
    171: ('HDMI CEC',       False), 172: ('VC TRST N',      False),
    173: ('HDMI SDA',       False), 174: ('VC TDI',         False),
    175: ('HDMI SCL',       False), 176: ('VC TMS',         False),
    177: ('RUN',            False), 178: ('VC TDO',         False),
    179: ('VDD CORE',       False), 180: ('VC TCK',         False),
    181: (GND,              False), 182: (GND,              False),
    183: (V1_8,             False), 184: (V1_8,             False),
    185: (V1_8,             False), 186: (V1_8,             False),
    187: (GND,              False), 188: (GND,              False),
    189: ('VDAC',           False), 190: ('VDAC',           False),
    191: (V3_3,             False), 192: (V3_3,             False),
    193: (V3_3,             False), 194: (V3_3,             False),
    195: (GND,              False), 196: (GND,              False),
    197: ('VBAT',           False), 198: ('VBAT',           False),
    199: ('VBAT',           False), 200: ('VBAT',           False),
    }

CM3_SODIMM = CM_SODIMM.copy()
CM3_SODIMM.update({
    4:  ('NC / SDX VREF',  False),
    6:  ('NC / SDX VREF',  False),
    8:  (GND,              False),
    10: ('NC / SDX CLK',   False),
    12: ('NC / SDX CMD',   False),
    14: (GND,              False),
    16: ('NC / SDX D0',    False),
    18: ('NC / SDX D1',    False),
    20: (GND,              False),
    22: ('NC / SDX D2',    False),
    24: ('NC / SDX D3',    False),
    88: ('HDMI HPD N 1V8', False),
    90: ('EMMC EN N 1V8',  False),
    })

# The following data is sourced from a combination of the following locations:
#
# http://elinux.org/RPi_HardwareHistory
# http://elinux.org/RPi_Low-level_peripherals
# https://git.drogon.net/?p=wiringPi;a=blob;f=wiringPi/wiringPi.c#l807
# https://www.raspberrypi.org/documentation/hardware/raspberrypi/revision-codes/README.md

PI_REVISIONS = {
    # rev     model    pcb_rev released soc        manufacturer ram   storage    usb eth wifi   bt     csi dsi headers                         board
    0x2:      ('B',    '1.0', '2012Q1', 'BCM2835', 'Egoman',    256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV1_P1},                REV1_BOARD,   ),
    0x3:      ('B',    '1.0', '2012Q3', 'BCM2835', 'Egoman',    256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV1_P1},                REV1_BOARD,   ),
    0x4:      ('B',    '2.0', '2012Q3', 'BCM2835', 'Sony',      256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5}, REV2_BOARD,   ),
    0x5:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Qisda',     256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5}, REV2_BOARD,   ),
    0x6:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Egoman',    256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5}, REV2_BOARD,   ),
    0x7:      ('A',    '2.0', '2013Q1', 'BCM2835', 'Egoman',    256,  'SD',      1,  0,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5}, A_BOARD,      ),
    0x8:      ('A',    '2.0', '2013Q1', 'BCM2835', 'Sony',      256,  'SD',      1,  0,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5}, A_BOARD,      ),
    0x9:      ('A',    '2.0', '2013Q1', 'BCM2835', 'Qisda',     256,  'SD',      1,  0,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5}, A_BOARD,      ),
    0xd:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Egoman',    512,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5}, REV2_BOARD,   ),
    0xe:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Sony',      512,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5}, REV2_BOARD,   ),
    0xf:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Qisda',     512,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P5': REV2_P5}, REV2_BOARD,   ),
    0x10:     ('B+',   '1.2', '2014Q3', 'BCM2835', 'Sony',      512,  'MicroSD', 4,  1,  False, False, 1,  1,  {'J8': PLUS_J8},                BPLUS_BOARD,  ),
    0x11:     ('CM',   '1.1', '2014Q2', 'BCM2835', 'Sony',      512,  'eMMC',    1,  0,  False, False, 2,  2,  {'SODIMM': CM_SODIMM},          CM_BOARD,     ),
    0x12:     ('A+',   '1.1', '2014Q4', 'BCM2835', 'Sony',      256,  'MicroSD', 1,  0,  False, False, 1,  1,  {'J8': PLUS_J8},                APLUS_BOARD,  ),
    0x13:     ('B+',   '1.2', '2015Q1', 'BCM2835', 'Egoman',    512,  'MicroSD', 4,  1,  False, False, 1,  1,  {'J8': PLUS_J8},                BPLUS_BOARD,  ),
    0x14:     ('CM',   '1.1', '2014Q2', 'BCM2835', 'Embest',    512,  'eMMC',    1,  0,  False, False, 2,  2,  {'SODIMM': CM_SODIMM},          CM_BOARD,     ),
    0x15:     ('A+',   '1.1', '2014Q4', 'BCM2835', 'Embest',    256,  'MicroSD', 1,  0,  False, False, 1,  1,  {'J8': PLUS_J8},                APLUS_BOARD,  ),
    }


# ANSI color codes, for the pretty printers (nothing comprehensive, just enough
# for our purposes)

class Style(object):
    def __init__(self, color=None):
        self.color = self._term_supports_color() if color is None else bool(color)
        self.effects = {
            'reset':  0,
            'bold':   1,
            'normal': 22,
            }
        self.colors = {
            'black':   0,
            'red':     1,
            'green':   2,
            'yellow':  3,
            'blue':    4,
            'magenta': 5,
            'cyan':    6,
            'white':   7,
            'default': 9,
            }

    @staticmethod
    def _term_supports_color():
        try:
            stdout_fd = sys.stdout.fileno()
        except IOError:
            return False
        else:
            is_a_tty = os.isatty(stdout_fd)
            is_windows = sys.platform.startswith('win')
            return is_a_tty and not is_windows

    @classmethod
    def from_style_content(cls, format_spec):
        specs = set(format_spec.split())
        style = specs & {'mono', 'color'}
        content = specs - style
        if len(style) > 1:
            raise ValueError('cannot specify both mono and color styles')
        try:
            style = style.pop()
        except KeyError:
            style = 'color' if cls._term_supports_color() else 'mono'
        if len(content) > 1:
            raise ValueError('cannot specify more than one content element')
        try:
            content = content.pop()
        except KeyError:
            content = 'full'
        return cls(style == 'color'), content

    def __call__(self, format_spec):
        specs = format_spec.split()
        codes = []
        fore = True
        for spec in specs:
            if spec == 'on':
                fore = False
            else:
                try:
                    codes.append(self.effects[spec])
                except KeyError:
                    try:
                        if fore:
                            codes.append(30 + self.colors[spec])
                        else:
                            codes.append(40 + self.colors[spec])
                    except KeyError:
                        raise ValueError(
                            'invalid format specification "%s"' % spec)
        if self.color:
            return '\x1b[%sm' % (';'.join(str(code) for code in codes))
        else:
            return ''

    def __format__(self, format_spec):
        if format_spec == '':
            return 'color' if self.color else 'mono'
        else:
            return self(format_spec)


class PinInfo(namedtuple('PinInfo', (
    'number',
    'function',
    'pull_up',
    'row',
    'col',
    ))):
    """
    This class is a :func:`~collections.namedtuple` derivative used to
    represent information about a pin present on a GPIO header. The following
    attributes are defined:

    .. attribute:: number

        An integer containing the physical pin number on the header (starting
        from 1 in accordance with convention).

    .. attribute:: function

        A string describing the function of the pin. Some common examples
        include "GND" (for pins connecting to ground), "3V3" (for pins which
        output 3.3 volts), "GPIO9" (for GPIO9 in the Broadcom numbering
        scheme), etc.

    .. attribute:: pull_up

        A bool indicating whether the pin has a physical pull-up resistor
        permanently attached (this is usually :data:`False` but GPIO2 and GPIO3
        are *usually* :data:`True`). This is used internally by gpiozero to
        raise errors when pull-down is requested on a pin with a physical
        pull-up resistor.

    .. attribute:: row

        An integer indicating on which row the pin is physically located in
        the header (1-based)

    .. attribute:: col

        An integer indicating in which column the pin is physically located
        in the header (1-based)
    """
    __slots__ = () # workaround python issue #24931


class HeaderInfo(namedtuple('HeaderInfo', (
    'name',
    'rows',
    'columns',
    'pins',
    ))):
    """
    This class is a :func:`~collections.namedtuple` derivative used to
    represent information about a pin header on a board. The object can be used
    in a format string with various custom specifications::

        from gpiozero import *

        print('{0}'.format(pi_info().headers['J8']))
        print('{0:full}'.format(pi_info().headers['J8']))
        print('{0:col2}'.format(pi_info().headers['P1']))
        print('{0:row1}'.format(pi_info().headers['P1']))

    "color" and "mono" can be prefixed to format specifications to force the
    use of `ANSI color codes`_. If neither is specified, ANSI codes will only
    be used if stdout is detected to be a tty::

        print('{0:color row2}'.format(pi_info().headers['J8'])) # force use of ANSI codes
        print('{0:mono row2}'.format(pi_info().headers['P1'])) # force plain ASCII

    The following attributes are defined:

    .. automethod:: pprint

    .. attribute:: name

        The name of the header, typically as it appears silk-screened on the
        board (e.g. "P1" or "J8").

    .. attribute:: rows

        The number of rows on the header.

    .. attribute:: columns

        The number of columns on the header.

    .. attribute:: pins

        A dictionary mapping physical pin numbers to :class:`PinInfo` tuples.

    .. _ANSI color codes: https://en.wikipedia.org/wiki/ANSI_escape_code
    """
    __slots__ = () # workaround python issue #24931

    def _func_style(self, function, style):
        if function == V5:
            return style('bold red')
        elif function in (V3_3, V1_8):
            return style('bold cyan')
        elif function in (GND, NC):
            return style('bold black')
        elif function.startswith('GPIO') and function[4:].isdigit():
            return style('bold green')
        else:
            return style('yellow')

    def _format_full(self, style):
        Cell = namedtuple('Cell', ('content', 'align', 'style'))

        lines = []
        for row in range(self.rows):
            line = []
            for col in range(self.columns):
                pin = (row * self.columns) + col + 1
                try:
                    pin = self.pins[pin]
                    cells = [
                        Cell(pin.function, '><'[col % 2], self._func_style(pin.function, style)),
                        Cell('(%d)' % pin.number, '><'[col % 2], ''),
                        ]
                    if col % 2:
                        cells = reversed(cells)
                    line.extend(cells)
                except KeyError:
                    line.append(Cell('', '<', ''))
            lines.append(line)
        cols = list(zip(*lines))
        col_lens = [max(len(cell.content) for cell in col) for col in cols]
        lines = [
            ' '.join(
                '{cell.style}{cell.content:{cell.align}{width}s}{style:reset}'.format(
                    cell=cell, width=width, style=style)
                for cell, width, align in zip(line, col_lens, cycle('><')))
            for line in lines
            ]
        return '\n'.join(lines)

    def _format_pin(self, pin, style):
        return ''.join((
            style('on black'),
            (
                ' ' if pin is None else
                self._func_style(pin.function, style) +
                ('1' if pin.number == 1 else 'o')
                ),
            style('reset')
            ))

    def _format_row(self, row, style):
        if row > self.rows:
            raise ValueError('invalid row %d for header %s' % (row, self.name))
        start_pin = (row - 1) * self.columns + 1
        return ''.join(
            self._format_pin(pin, style)
            for n in range(start_pin, start_pin + self.columns)
            for pin in (self.pins.get(n),)
            )

    def _format_col(self, col, style):
        if col > self.columns:
            raise ValueError('invalid col %d for header %s' % (col, self.name))
        return ''.join(
            self._format_pin(pin, style)
            for n in range(col, self.rows * self.columns + 1, self.columns)
            for pin in (self.pins.get(n),)
            )

    def __format__(self, format_spec):
        style, content = Style.from_style_content(format_spec)
        if content == 'full':
            return self._format_full(style)
        elif content.startswith('row') and content[3:].isdigit():
            return self._format_row(int(content[3:]), style)
        elif content.startswith('col') and content[3:].isdigit():
            return self._format_col(int(content[3:]), style)

    def pprint(self, color=None):
        """
        Pretty-print a diagram of the header pins.

        If *color* is :data:`None` (the default, the diagram will include ANSI
        color codes if stdout is a color-capable terminal). Otherwise *color*
        can be set to :data:`True` or :data:`False` to force color or
        monochrome output.
        """
        print('{0:{style} full}'.format(self, style=Style(color)))


class PiBoardInfo(namedtuple('PiBoardInfo', (
    'revision',
    'model',
    'pcb_revision',
    'released',
    'soc',
    'manufacturer',
    'memory',
    'storage',
    'usb',
    'ethernet',
    'wifi',
    'bluetooth',
    'csi',
    'dsi',
    'headers',
    'board',
    ))):
    """
    This class is a :func:`~collections.namedtuple` derivative used to
    represent information about a particular model of Raspberry Pi. While it is
    a tuple, it is strongly recommended that you use the following named
    attributes to access the data contained within. The object can be used
    in format strings with various custom format specifications::

        from gpiozero import *

        print('{0}'.format(pi_info()))
        print('{0:full}'.format(pi_info()))
        print('{0:board}'.format(pi_info()))
        print('{0:specs}'.format(pi_info()))
        print('{0:headers}'.format(pi_info()))

    "color" and "mono" can be prefixed to format specifications to force the
    use of `ANSI color codes`_. If neither is specified, ANSI codes will only
    be used if stdout is detected to be a tty::

        print('{0:color board}'.format(pi_info())) # force use of ANSI codes
        print('{0:mono board}'.format(pi_info())) # force plain ASCII

    .. _ANSI color codes: https://en.wikipedia.org/wiki/ANSI_escape_code

    .. automethod:: physical_pin

    .. automethod:: physical_pins

    .. automethod:: pprint

    .. automethod:: pulled_up

    .. automethod:: to_gpio

    .. attribute:: revision

        A string indicating the revision of the Pi. This is unique to each
        revision and can be considered the "key" from which all other
        attributes are derived. However, in itself the string is fairly
        meaningless.

    .. attribute:: model

        A string containing the model of the Pi (for example, "B", "B+", "A+",
        "2B", "CM" (for the Compute Module), or "Zero").

    .. attribute:: pcb_revision

        A string containing the PCB revision number which is silk-screened onto
        the Pi (on some models).

        .. note::

            This is primarily useful to distinguish between the model B
            revision 1.0 and 2.0 (not to be confused with the model 2B) which
            had slightly different pinouts on their 26-pin GPIO headers.

    .. attribute:: released

        A string containing an approximate release date for this revision of
        the Pi (formatted as yyyyQq, e.g. 2012Q1 means the first quarter of
        2012).

    .. attribute:: soc

        A string indicating the SoC (`system on a chip`_) that this revision
        of the Pi is based upon.

    .. attribute:: manufacturer

        A string indicating the name of the manufacturer (usually "Sony" but a
        few others exist).

    .. attribute:: memory

        An integer indicating the amount of memory (in Mb) connected to the
        SoC.

        .. note::

            This can differ substantially from the amount of RAM available
            to the operating system as the GPU's memory is shared with the
            CPU. When the camera module is activated, at least 128Mb of RAM
            is typically reserved for the GPU.

    .. attribute:: storage

        A string indicating the type of bootable storage used with this
        revision of Pi, e.g. "SD", "MicroSD", or "eMMC" (for the Compute
        Module).

    .. attribute:: usb

        An integer indicating how many USB ports are physically present on
        this revision of the Pi.

        .. note::

            This does *not* include the micro-USB port used to power the Pi.

    .. attribute:: ethernet

        An integer indicating how many Ethernet ports are physically present
        on this revision of the Pi.

    .. attribute:: wifi

        A bool indicating whether this revision of the Pi has wifi built-in.

    .. attribute:: bluetooth

        A bool indicating whether this revision of the Pi has bluetooth
        built-in.

    .. attribute:: csi

        An integer indicating the number of CSI (camera) ports available on
        this revision of the Pi.

    .. attribute:: dsi

        An integer indicating the number of DSI (display) ports available on
        this revision of the Pi.

    .. attribute:: headers

        A dictionary which maps header labels to :class:`HeaderInfo` tuples.
        For example, to obtain information about header P1 you would query
        ``headers['P1']``. To obtain information about pin 12 on header J8 you
        would query ``headers['J8'].pins[12]``.

        A rendered version of this data can be obtained by using the
        :class:`PiBoardInfo` object in a format string::

            from gpiozero import *
            print('{0:headers}'.format(pi_info()))

    .. attribute:: board

        An ASCII art rendition of the board, primarily intended for console
        pretty-print usage. A more usefully rendered version of this data can
        be obtained by using the :class:`PiBoardInfo` object in a format
        string. For example::

            from gpiozero import *
            print('{0:board}'.format(pi_info()))

    .. _system on a chip: https://en.wikipedia.org/wiki/System_on_a_chip
    """
    __slots__ = () # workaround python issue #24931

    @classmethod
    def from_revision(cls, revision):
        if revision & 0x800000:
            # New-style revision, parse information from bit-pattern:
            #
            # MSB -----------------------> LSB
            # uuuuuuuuFMMMCCCCPPPPTTTTTTTTRRRR
            #
            # uuuuuuuu - Unused
            # F        - New flag (1=valid new-style revision, 0=old-style)
            # MMM      - Memory size (0=256, 1=512, 2=1024)
            # CCCC     - Manufacturer (0=Sony, 1=Egoman, 2=Embest, 3=Sony Japan, 4=Embest, 5=Stadium)
            # PPPP     - Processor (0=2835, 1=2836, 2=2837)
            # TTTTTTTT - Type (0=A, 1=B, 2=A+, 3=B+, 4=2B, 5=Alpha (??), 6=CM,
            #                  8=3B, 9=Zero, 10=CM3, 12=Zero W, 13=3B+, 14=3A+)
            # RRRR     - Revision (0, 1, 2, etc.)
            revcode_memory       = (revision & 0x700000) >> 20
            revcode_manufacturer = (revision & 0xf0000)  >> 16
            revcode_processor    = (revision & 0xf000)   >> 12
            revcode_type         = (revision & 0xff0)    >> 4
            revcode_revision     = (revision & 0x0f)
            try:
                model = {
                    0:  'A',
                    1:  'B',
                    2:  'A+',
                    3:  'B+',
                    4:  '2B',
                    6:  'CM',
                    8:  '3B',
                    9:  'Zero',
                    10: 'CM3',
                    12: 'Zero W',
                    13: '3B+',
                    14: '3A+',
                    16: 'CM3+',
                    17: '4B',
                    }.get(revcode_type, '???')
                if model in ('A', 'B'):
                    pcb_revision = {
                        0: '1.0', # is this right?
                        1: '1.0',
                        2: '2.0',
                        }.get(revcode_revision, 'Unknown')
                else:
                    pcb_revision = '1.%d' % revcode_revision
                soc = {
                    0: 'BCM2835',
                    1: 'BCM2836',
                    2: 'BCM2837',
                    3: 'BCM2711',
                    }.get(revcode_processor, 'Unknown')
                manufacturer = {
                    0: 'Sony',
                    1: 'Egoman',
                    2: 'Embest',
                    3: 'Sony Japan',
                    4: 'Embest',
                    5: 'Stadium',
                    }.get(revcode_manufacturer, 'Unknown')
                memory = {
                    0: 256,
                    1: 512,
                    2: 1024,
                    3: 2048,
                    4: 4096,
                    5: 8192,
                    }.get(revcode_memory, None)
                released = {
                    'A':      '2013Q1',
                    'B':      '2012Q1' if pcb_revision == '1.0' else '2012Q4',
                    'A+':     '2014Q4' if memory == 512 else '2016Q3',
                    'B+':     '2014Q3',
                    '2B':     '2015Q1' if pcb_revision in ('1.0', '1.1') else '2016Q3',
                    'CM':     '2014Q2',
                    '3B':     '2016Q1' if manufacturer in ('Sony', 'Embest') else '2016Q4',
                    'Zero':   '2015Q4' if pcb_revision == '1.2' else '2016Q2',
                    'CM3':    '2017Q1',
                    'Zero W': '2017Q1',
                    '3B+':    '2018Q1',
                    '3A+':    '2018Q4',
                    'CM3+':   '2019Q1',
                    '4B':     '2020Q2' if memory == 8192 else '2019Q2',
                    }.get(model, 'Unknown')
                storage = {
                    'A':    'SD',
                    'B':    'SD',
                    'CM':   'eMMC',
                    'CM3':  'eMMC / off-board',
                    'CM3+': 'eMMC / off-board',
                    }.get(model, 'MicroSD')
                usb = {
                    'A':      1,
                    'A+':     1,
                    'Zero':   1,
                    'Zero W': 1,
                    'B':      2,
                    'CM':     1,
                    'CM3':    1,
                    '3A+':    1,
                    'CM3+':   1,
                    }.get(model, 4)
                ethernet = {
                    'A':      0,
                    'A+':     0,
                    'Zero':   0,
                    'Zero W': 0,
                    'CM':     0,
                    'CM3':    0,
                    '3A+':    0,
                    'CM3+':   0,
                    }.get(model, 1)
                wifi = {
                    '3B':     True,
                    'Zero W': True,
                    '3B+':    True,
                    '3A+':    True,
                    '4B':     True,
                    }.get(model, False)
                bluetooth = {
                    '3B':     True,
                    'Zero W': True,
                    '3B+':    True,
                    '3A+':    True,
                    '4B':     True,
                    }.get(model, False)
                csi = {
                    'Zero':   0 if pcb_revision == '1.0' else 1,
                    'Zero W': 1,
                    'CM':     2,
                    'CM3':    2,
                    'CM3+':   2,
                    }.get(model, 1)
                dsi = {
                    'Zero':   0,
                    'Zero W': 0,
                    'CM':     2,
                    'CM3':    2,
                    'CM3+':   2,
                    }.get(model, csi)
                headers = {
                    'A':    {'P1': REV2_P1, 'P5': REV2_P5},
                    'B':    {'P1': REV1_P1} if pcb_revision == '1.0' else {'P1': REV2_P1, 'P5': REV2_P5},
                    'CM':   {'SODIMM': CM_SODIMM},
                    'CM3':  {'SODIMM': CM3_SODIMM},
                    'CM3+': {'SODIMM': CM3_SODIMM},
                    }.get(model, {'J8': PLUS_J8})
                board = {
                    'A':      A_BOARD,
                    'B':      REV1_BOARD if pcb_revision == '1.0' else REV2_BOARD,
                    'A+':     APLUS_BOARD,
                    'CM':     CM_BOARD,
                    'CM3':    CM_BOARD,
                    'CM3+':   CM_BOARD,
                    'Zero':   ZERO12_BOARD if pcb_revision == '1.2' else ZERO13_BOARD,
                    'Zero W': ZERO13_BOARD,
                    '3A+':    A3PLUS_BOARD,
                    '3B+':    B3PLUS_BOARD,
                    '4B':     B4_BOARD,
                    }.get(model, BPLUS_BOARD)
            except KeyError:
                raise PinUnknownPi('unable to parse new-style revision "%x"' % revision)
        else:
            # Old-style revision, use the lookup table
            try:
                (
                    model,
                    pcb_revision,
                    released,
                    soc,
                    manufacturer,
                    memory,
                    storage,
                    usb,
                    ethernet,
                    wifi,
                    bluetooth,
                    csi,
                    dsi,
                    headers,
                    board,
                    ) = PI_REVISIONS[revision]
            except KeyError:
                raise PinUnknownPi('unknown old-style revision "%x"' % revision)
        headers = {
            header: HeaderInfo(name=header, rows=max(header_data) // 2, columns=2, pins={
                number: PinInfo(
                    number=number, function=function, pull_up=pull_up,
                    row=row + 1, col=col + 1)
                for number, (function, pull_up) in header_data.items()
                for row, col in (divmod(number - 1, 2),)
                })
            for header, header_data in headers.items()
            }
        return cls(
            '%04x' % revision,
            model,
            pcb_revision,
            released,
            soc,
            manufacturer,
            memory,
            storage,
            usb,
            ethernet,
            wifi,
            bluetooth,
            csi,
            dsi,
            headers,
            board,
            )

    def physical_pins(self, function):
        """
        Return the physical pins supporting the specified *function* as tuples
        of ``(header, pin_number)`` where *header* is a string specifying the
        header containing the *pin_number*. Note that the return value is a
        :class:`set` which is not indexable. Use :func:`physical_pin` if you
        are expecting a single return value.

        :param str function:
            The pin function you wish to search for. Usually this is something
            like "GPIO9" for Broadcom GPIO pin 9, or "GND" for all the pins
            connecting to electrical ground.
        """
        return {
            (header, pin.number)
            for (header, info) in self.headers.items()
            for pin in info.pins.values()
            if pin.function == function
            }

    def physical_pin(self, function):
        """
        Return the physical pin supporting the specified *function*. If no pins
        support the desired *function*, this function raises :exc:`PinNoPins`.
        If multiple pins support the desired *function*, :exc:`PinMultiplePins`
        will be raised (use :func:`physical_pins` if you expect multiple pins
        in the result, such as for electrical ground).

        :param str function:
            The pin function you wish to search for. Usually this is something
            like "GPIO9" for Broadcom GPIO pin 9.
        """
        result = self.physical_pins(function)
        if len(result) > 1:
            raise PinMultiplePins('multiple pins can be used for %s' % function)
        elif result:
            return result.pop()
        else:
            raise PinNoPins('no pins can be used for %s' % function)

    def pulled_up(self, function):
        """
        Returns a bool indicating whether a physical pull-up is attached to
        the pin supporting the specified *function*. Either :exc:`PinNoPins`
        or :exc:`PinMultiplePins` may be raised if the function is not
        associated with a single pin.

        :param str function:
            The pin function you wish to determine pull-up for. Usually this is
            something like "GPIO9" for Broadcom GPIO pin 9.
        """
        try:
            header, number = self.physical_pin(function)
        except PinNoPins:
            return False
        else:
            return self.headers[header].pins[number].pull_up

    def to_gpio(self, spec):
        """
        Parses a pin *spec*, returning the equivalent Broadcom GPIO port number
        or raising a :exc:`ValueError` exception if the spec does not represent
        a GPIO port.

        The *spec* may be given in any of the following forms:

        * An integer, which will be accepted as a GPIO number
        * 'GPIOn' where n is the GPIO number
        * 'WPIn' where n is the `wiringPi`_ pin number
        * 'BCMn' where n is the GPIO number (alias of GPIOn)
        * 'BOARDn' where n is the physical pin number on the main header
        * 'h:n' where h is the header name and n is the physical pin number
          (for example J8:5 is physical pin 5 on header J8, which is the main
          header on modern Raspberry Pis)

        .. _wiringPi: http://wiringpi.com/pins/
        """
        if isinstance(spec, int):
            if not 0 <= spec < 54:
                raise PinInvalidPin('invalid GPIO port %d specified '
                                    '(range 0..53) ' % spec)
            return spec
        else:
            if isinstance(spec, bytes):
                spec = spec.decode('ascii')
            spec = spec.upper()
            if spec.isdigit():
                return self.to_gpio(int(spec))
            if spec.startswith('GPIO') and spec[4:].isdigit():
                return self.to_gpio(int(spec[4:]))
            elif spec.startswith('BCM') and spec[3:].isdigit():
                return self.to_gpio(int(spec[3:]))
            elif spec.startswith('WPI') and spec[3:].isdigit():
                main_head = 'P1' if 'P1' in self.headers else 'J8'
                try:
                    return self.to_gpio({
                        0:  '%s:11' % main_head,
                        1:  '%s:12' % main_head,
                        2:  '%s:13' % main_head,
                        3:  '%s:15' % main_head,
                        4:  '%s:16' % main_head,
                        5:  '%s:18' % main_head,
                        6:  '%s:22' % main_head,
                        7:  '%s:7'  % main_head,
                        8:  '%s:3'  % main_head,
                        9:  '%s:5'  % main_head,
                        10: '%s:24' % main_head,
                        11: '%s:26' % main_head,
                        12: '%s:19' % main_head,
                        13: '%s:21' % main_head,
                        14: '%s:23' % main_head,
                        15: '%s:8'  % main_head,
                        16: '%s:10' % main_head,
                        17: 'P5:3',
                        18: 'P5:4',
                        19: 'P5:5',
                        20: 'P5:6',
                        21: '%s:29' % main_head,
                        22: '%s:31' % main_head,
                        23: '%s:33' % main_head,
                        24: '%s:35' % main_head,
                        25: '%s:37' % main_head,
                        26: '%s:32' % main_head,
                        27: '%s:36' % main_head,
                        28: '%s:38' % main_head,
                        29: '%s:40' % main_head,
                        30: '%s:27' % main_head,
                        31: '%s:28' % main_head,
                        }[int(spec[3:])])
                except KeyError:
                    raise PinInvalidPin('%s is not a valid wiringPi pin' % spec)
            elif ':' in spec:
                header, pin = spec.split(':', 1)
                if pin.isdigit():
                    try:
                        header = self.headers[header]
                    except KeyError:
                        raise PinInvalidPin(
                            'there is no %s header on this Pi' % header)
                    try:
                        function = header.pins[int(pin)].function
                    except KeyError:
                        raise PinInvalidPin(
                            'no such pin %s on header %s' % (pin, header.name))
                    if function.startswith('GPIO') and function[4:].isdigit():
                        return self.to_gpio(int(function[4:]))
                    else:
                        raise PinInvalidPin('%s is not a GPIO pin' % spec)
            elif spec.startswith('BOARD') and spec[5:].isdigit():
                main_head = ({'P1', 'J8', 'SODIMM'} & set(self.headers)).pop()
                return self.to_gpio('%s:%s' % (main_head, spec[5:]))
            raise PinInvalidPin('%s is not a valid pin spec' % spec)

    def __repr__(self):
        return '{cls}({fields})'.format(
            cls=self.__class__.__name__,
            fields=', '.join(
                (
                    '{name}=...' if name in ('headers', 'board') else
                    '{name}={value!r}').format(name=name, value=value)
                for name, value in zip(self._fields, self)
                )
            )

    def __format__(self, format_spec):
        style, content = Style.from_style_content(format_spec)
        if content == 'full':
            return dedent("""\
                {self:{style} board}

                {self:{style} specs}

                {self:{style} headers}"""
                ).format(self=self, style=style)
        elif content == 'board':
            kw = self._asdict()
            kw.update({
                name: header
                for name, header in self.headers.items()
                })
            return self.board.format(style=style, **kw)
        elif content == 'specs':
            return dedent("""\
                {style:bold}Revision           {style:reset}: {revision}
                {style:bold}SoC                {style:reset}: {soc}
                {style:bold}RAM                {style:reset}: {memory}Mb
                {style:bold}Storage            {style:reset}: {storage}
                {style:bold}USB ports          {style:reset}: {usb} {style:yellow}(excluding power){style:reset}
                {style:bold}Ethernet ports     {style:reset}: {ethernet}
                {style:bold}Wi-fi              {style:reset}: {wifi}
                {style:bold}Bluetooth          {style:reset}: {bluetooth}
                {style:bold}Camera ports (CSI) {style:reset}: {csi}
                {style:bold}Display ports (DSI){style:reset}: {dsi}"""
                ).format(style=style, **self._asdict())
        elif content == 'headers':
            return '\n\n'.join(
                dedent("""\
                {style:bold}{header.name}{style:reset}:
                {header:{style} full}"""
                ).format(header=header, style=style)
                for header in sorted(self.headers.values(), key=attrgetter('name'))
                )

    def pprint(self, color=None):
        """
        Pretty-print a representation of the board along with header diagrams.

        If *color* is :data:`None` (the default), the diagram will include ANSI
        color codes if stdout is a color-capable terminal. Otherwise *color*
        can be set to :data:`True` or :data:`False` to force color or monochrome
        output.
        """
        print('{0:{style} full}'.format(self, style=Style(color)))


def pi_info(revision=None):
    """
    Returns a :class:`PiBoardInfo` instance containing information about a
    *revision* of the Raspberry Pi.

    :param str revision:
        The revision of the Pi to return information about. If this is omitted
        or :data:`None` (the default), then the library will attempt to determine
        the model of Pi it is running on and return information about that.
    """
    if revision is None:
        if Device.pin_factory is None:
            Device.pin_factory = Device._default_pin_factory()
        result = Device.pin_factory.pi_info
        if result is None:
            raise PinUnknownPi('The default pin_factory is not attached to a Pi')
        else:
            return result
    else:
        if isinstance(revision, bytes):
            revision = revision.decode('ascii')
        if isinstance(revision, str):
            revision = int(revision, base=16)
        else:
            # be nice to people passing an int (or something numeric anyway)
            revision = int(revision)
        return PiBoardInfo.from_revision(revision)
