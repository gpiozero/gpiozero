# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2021 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2018-2021 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2020 chrisruk <chrisrichardsonuk@gmail.com>
# Copyright (c) 2016-2019 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

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
{style:white on green}| {style:black on white} Wi {style:white on green}                   {POE:{style} row1}{style:on green}   {style:black on white}+===={style:reset}
{style:white on green}| {style:black on white} Fi {style:white on green} {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal} {POE:{style} row2}{style:on green}      |{style:reset}
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
{style:white on green}| {style:black on white} Wi {style:white on green}                   {POE:{style} row1}{style:on green} {style:black on white}+======{style:reset}
{style:white on green}| {style:black on white} Fi {style:white on green} {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal} {POE:{style} row2}{style:normal white on green}      |{style:reset}
{style:white on green}|        {style:black on white},----.{style:on green} {style:white on black}+---+{style:on green}         {style:blue on white}+===={style:reset}
{style:white on green}| {style:on black}|D|{style:on green}    {style:black on white}|SoC |{style:on green} {style:white on black}|RAM|{style:on green}         {style:blue on white}|USB3{style:reset}
{style:white on green}| {style:on black}|S|{style:on green}    {style:black on white}|    |{style:on green} {style:white on black}|   |{style:on green}         {style:blue on white}+===={style:reset}
{style:white on green}| {style:on black}|I|{style:on green}    {style:black on white}`----'{style:white on green} {style:white on black}+---+{style:on green}            |{style:reset}
{style:white on green}|                   {style:on black}|C|{style:on green}       {style:black on white}+===={style:reset}
{style:white on green}|                   {style:on black}|S|{style:on green}       {style:black on white}|USB2{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}   {style:black on white}|hd|{style:white on green}   {style:black on white}|hd|{style:white on green} {style:on black}|I||A|{style:on green}    {style:black on white}+===={style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}---{style:black on white}|m0|{style:white on green}---{style:black on white}|m1|{style:white on green}----{style:on black}|V|{style:on green}-------'{style:reset}"""

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
{style:white on green},--{J8:{style} col2}{style:white on green}---.{style:reset}
{style:white on green}|  {J8:{style} col1}{style:white on green}J8 |{style:reset}
{style:black on white}---+{style:white on green}                      |{style:reset}
{style:black on white} sd|{style:white on green}      {style:white on black}+---+{style:white on green}  {style:bold}Pi{model:6s}{style:normal} |{style:reset}
{style:black on white}---+{style:white on green}      {style:white on black}|SoC|{style:white on green}  {style:bold}V{pcb_revision:3s}{style:normal}     |{style:reset}
{style:white on green}| {style:black on white}hdmi{style:white on green}    {style:white on black}+---+{style:white on green}   {style:black on white}usb{style:on green} {style:black on white}pwr{style:white on green} |{style:reset}
{style:white on green}`-{style:black on white}|  |{style:white on green}------------{style:black on white}| |{style:white on green}-{style:black on white}| |{style:white on green}-'{style:reset}"""

ZERO13_BOARD = """\
{style:white on green},--{J8:{style} col2}{style:white on green}---.{style:reset}
{style:white on green}|  {J8:{style} col1}{style:white on green}J8 |{style:reset}
{style:black on white}---+{style:white on green}                     {style:black on white}|c{style:reset}
{style:black on white} sd|{style:white on green}      {style:white on black}+---+{style:white on green} {style:bold}Pi{model:6s} {style:normal black on white}|s{style:reset}
{style:black on white}---+{style:white on green}      {style:white on black}|SoC|{style:white on green} {style:bold}V{pcb_revision:3s}{style:normal}     {style:black on white}|i{style:reset}
{style:white on green}| {style:black on white}hdmi{style:white on green}    {style:white on black}+---+{style:white on green}   {style:black on white}usb{style:on green} {style:black on white}pwr{style:white on green} |{style:reset}
{style:white on green}`-{style:black on white}|  |{style:white on green}------------{style:black on white}| |{style:white on green}-{style:black on white}| |{style:white on green}-'{style:reset}"""

ZERO2_BOARD = """\
{style:white on green},--{J8:{style} col2}{style:white on green}---.{style:reset}
{style:white on green}|  {J8:{style} col1}{style:white on green}J8 |{style:reset}
{style:black on white}---+{style:white on green}     {style:normal on black}+----+{style:on green} {style:bold}Pi{model:6s} {style:normal black on white}|c{style:reset}
{style:black on white} sd|{style:white on green}     {style:white on black}|SoC |{style:white on green} {style:black on white} Wi {style:bold white on green}V{pcb_revision:3s} {style:normal black on white}|s{style:reset}
{style:black on white}---+{style:white on green}     {style:white on black}|    |{style:white on green} {style:black on white} Fi {style:on green}     {style:on white}|i{style:reset}
{style:white on green}| {style:black on white}hdmi{style:white on green}   {style:white on black}+----+{style:white on green}   {style:black on white}usb{style:on green} {style:black on white}pwr{style:white on green} |{style:reset}
{style:white on green}`-{style:black on white}|  |{style:white on green}------------{style:black on white}| |{style:white on green}-{style:black on white}| |{style:white on green}-'{style:reset}
"""

CM_BOARD = """\
{style:white on green}+---------------------------------------+{style:reset}
{style:white on green}| {style:yellow on black}O{style:bold white on green}  Raspberry Pi {model:4s}                {style:normal yellow on black}O{style:white on green} |{style:reset}
 {style:white on green})   Version {pcb_revision:3s}     {style:on black}+---+{style:on green}             ({style:reset}
{style:white on green}|                    {style:on black}|SoC|{style:on green}              |{style:reset}
 {style:white on green})                   {style:on black}+---+{style:on green}             ({style:reset}
{style:white on green}| {style:on black}O{style:on green}   _                               {style:on black}O{style:on green} |{style:reset}
{style:white on green}||||||{style:reset} {style:white on green}||||||||||||||||||||||||||||||||||{style:reset}"""

CM3PLUS_BOARD = """\
{style:white on green}+---------------------------------------+{style:reset}
{style:white on green}| {style:yellow on black}O{style:bold white on green}  Raspberry Pi {model:4s}                {style:normal yellow on black}O{style:white on green} |{style:reset}
 {style:white on green})   Version {pcb_revision:3s}     {style:black on white},---.{style:white on green}             ({style:reset}
{style:white on green}|                    {style:black on white}|SoC|{style:white on green}              |{style:reset}
 {style:white on green})                   {style:black on white}`---'{style:white on green}             ({style:reset}
{style:white on green}| {style:on black}O{style:on green}   _                               {style:on black}O{style:on green} |{style:reset}
{style:white on green}||||||{style:reset} {style:white on green}||||||||||||||||||||||||||||||||||{style:reset}"""

CM4_BOARD = """\
{style:white on green},--{style:black on white}csi1{style:white on green}---{style:black on white}dsi0{style:white on green}---{style:black on white}dsi1{style:white on green}-----------{style:bold},-------------.{style:normal}-----------.{style:reset}
{style:white on green}|  {style:black on white}----{style:white on green}   {style:black on white}----{style:white on green}   {style:black on white}----{style:white on green}  J2{J2:{style} col2}{style:bold white on green}|{style:yellow}O           O{style:white}|{style:normal}           |{style:reset}
{style:white on green}{style:black on white}c|{style:white on green} {style:bold yellow}O  {style:white}Pi {model:4s} Rev {pcb_revision:3s}{style:normal}    {J2:{style} col1}{style:bold white on green}|       {style:normal black on white} Wi {style:white on green}  {style:bold}|{style:normal}       {style:bold yellow}O{style:normal white}   |{style:reset}
{style:white on green}{style:black on white}s|{style:white on green}    {style:bold}IO Board{style:normal}                  {style:bold}|       {style:normal black on white} Fi {style:white on green}  {style:bold}|{style:normal}           |{style:reset}
{style:white on green}{style:black on white}i|{style:white on green}           J6{J6:{style} col2}{style:bold white on green}               |         {style:normal white on black}+--+{style:on green}{style:bold}|  {style:normal white on black}|P|{style:on green}      |{style:reset}
{style:white on green}| J8           {J6:{style} col1}{style:bold white on green}               |  {style:normal black on white},----.{style:on green} {style:white on black}|eM|{style:bold on green}|  {style:normal white on black}}}-{{{style:on green}      |{style:reset}
{style:white on green}|{style:bold yellow}O{J8:{style} col2}{style:white on green}   {style:bold yellow}O{style:white}      |  {style:normal black on white}|SoC |{style:on green} {style:white on black}|MC|{style:bold on green}|  {style:normal white on black}|C|{style:on green}      |{style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}   PoE    {style:bold}|  {style:normal black on white}|    |{style:on green} {style:white on black}+--+{style:bold on green}|  {style:normal white on black}|I|{style:on green}      |{style:reset}
{style:white on green}| {style:black on white},---.{style:white on green}                  {POE:{style} row1}{style:bold white on green}     |  {style:normal black on white}`----'{style:white on green}     {style:bold}|  {style:normal white on black}|e|{style:on green}      |{style:reset}
{style:white on green}|{style:black on white}( ={style:on green}O{style:on white} |{style:white on green}                  {POE:{style} row2}{style:bold white on green}     |  {style:normal white on black}+----+{style:on green}     {style:bold}|{style:normal}           |{style:reset}
{style:white on green}| {style:black on white}) + |{style:white on green}                         {style:bold}|{style:yellow}O {style:normal white on black}|RAM |{style:on green}    {style:bold yellow}O{style:white}|{style:normal}           |{style:reset}
{style:white on green}|{style:black on white}( ={style:on green}O{style:on white} |{style:white on green}                         {style:bold}`--{style:normal white on black}+----+{style:bold on green}-----'{style:normal}           |{style:reset}
{style:white on green}| {style:black on white}`---'{style:white on green}                                                   |{style:reset}
{style:white on green}|                                                         |{style:reset}
{style:white on green}|                                                         |{style:reset}
{style:white on green}|  {style:bold yellow}O                       {style:normal black on white}|Net |{style:on green} {style:black on white}|USB|{style:on green}     {style:black on white}|uSD|{style:white on green}     {style:bold yellow}O{style:normal white on black}|p|{style:on green}|{style:reset}
{style:white on green}|{style:bold yellow}O   {style:normal black on white}|HDMI|{style:on green}   {style:black on white}|HDMI|{style:white on green}     {style:bold yellow}O {style:normal black on white}|    |{style:on green} {style:black on white}| 2 |{style:on green} {style:black on white}usb{style:white on green} {style:black on white}|   |{style:white on green}      {style:on black}|w|{style:on green}|{style:reset}
{style:white on green}`----{style:black on white}| 0  |{style:white on green}---{style:black on white}| 1  |{style:white on green}-------{style:black on white}|    |{style:white on green}-{style:black on white}|   |{style:white on green}-{style:black on white}| |{style:white on green}------------{style:white on black}|r|{style:on green}'{style:reset}"""

P400_BOARD = """\
    {style:white on red},------+----+----+----+----+---+--+--+--+--------------------+---.{style:reset}
  {style:white on red},'       |{style:white on black}Net {style:white on red}|{style:white on black}USB {style:white on red}|{style:cyan on black}USB {style:white on red}|{style:cyan on black}USB {style:white on red}|{style:white on black}pwr{style:white on red}|{style:white on black}hd{style:white on red}|{style:white on black}hd{style:white on red}|{style:white on black}sd{style:white on red}|{J8:{style} col2}{style:white on red}|    `.{style:reset}
 {style:white on red}/     {style:black}=={style:white}  |{style:white on black}    {style:white on red}|{style:white on black} 2  {style:white on red}|{style:cyan on black} 3  {style:white on red}|{style:cyan on black} 3  {style:white on red}|{style:white on black}   {style:white on red}|{style:white on black}m1{style:white on red}|{style:white on black}m0{style:white on red}|{style:white on black}  {style:white on red}|{J8:{style} col1}{style:white on red}|      \\{style:reset}
{style:black on white},------------------------------------------------------------------------.{style:reset}
{style:black on white}|  ___ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ ____ {style:bold on white}o o {style:green}o{style:normal black}____  |{style:reset}
{style:black on white}| |Esc|F1{style:red}11{style:black}|F2{style:red}12{style:black}|F3  |F4  |F5  |F6  |F7  |F8  |F9  |F10{style:red}o{style:black}|NumL|Pt{style:red}Sq{style:black}|Dl{style:red}In{style:black}| |{style:reset}
{style:black on white}|  ___ ___ ____ ____ ____ ____ ____ ___ ____ ____ ____ ___ ____ _______  |{style:reset}
{style:black on white}| |¬  |!  |"   |£   |$   |%   |^   |& {style:red}7{style:black}|*  {style:red}8{style:black}|(  {style:red}9{style:black}|)  {style:red}*{style:black}|_  |+   |BkSpc  | |{style:reset}
{style:black on white}| |` ||1  |2   |3   |4   |5   |6   |7  |8   |9   |0   |-  |=   |<--    | |{style:reset}
{style:black on white}|  _____ ___ ____ ____ ____ ____ ____ ___ ____ ____ ____ ____ __ ______  |{style:reset}
{style:black on white}| |Tab  |Q  |W   |E   |R   |T   |Y   |U {style:red}4{style:black}|I  {style:red}5{style:black}|O  {style:red}6{style:black}|P  {style:red}-{style:black}|{{   |}} |Enter | |{style:reset}
{style:black on white}| |->|  |   |    |    |    |    |    |   |    |    |    |[   |] |<-'   | |{style:reset}
{style:black on white}|  ______ ____ ____ ____ ____ ____ ____ ___ ____ ____ ____ ____ __     | |{style:reset}
{style:black on white}| |Caps  |A   |S   |D   |F   |G   |H   |J {style:red}1{style:black}|K  {style:red}2{style:black}|L  {style:red}3{style:black}|:  {style:red}+{style:black}|@   |~ |    | |{style:reset}
{style:black on white}| |Lock  |    |    |    |    |    |    |   |    |    |;   |'   |# |    | |{style:reset}
{style:black on white}|  _____ ___ ___ ____ ____ ____ ____ ____ ___ ____ ____ ____ __________  |{style:reset}
{style:black on white}| |Shift||  |Z  |X   |C   |V   |B   |N   |M {style:red}0{style:black}|<   |>  {style:red}.{style:black}|?  {style:red}/{style:black}|Shift     | |{style:reset}
{style:black on white}| |^    |\\  |   |    |    |    |    |    |   |,   |.   |/   |^         | |{style:reset}
{style:black on white}|  ____ ___ ____ ____ _______________________ ____ ____      _____       |{style:reset}
{style:black on white}| |Ctrl|{style:red}Fn{style:black} | {style:red}**{style:black} |Alt |                       |Alt |Ctrl|____|^{style:red}PgUp{style:black}|____  |{style:reset}
{style:black on white}| |    |   | {style:red}{{}}{style:black} |    |                       |    |    |<{style:red}Hom{style:black}|v{style:red}PgDn{style:black}|>{style:red}End{style:black}| |{style:reset}
{style:black on white}`------------------------------------------------------------------------'{style:reset}
                                                 Raspberry Pi {style:bold red}{model}{style:reset} Rev {pcb_revision}"""

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

PLUS_POE = {
    1: ('TR01', False), 2: ('TR00', False),
    3: ('TR03', False), 4: ('TR02', False),
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

CM4_J6 = {
    1: ('1-2 CAM0+DISP0', False), 2: ('1-2 CAM0+DISP0', False),
    3: ('3-4 CAM0+DISP0', False), 4: ('3-4 CAM0+DISP0', False),
    }

CM4_J2 = {
    1:  ('1-2 DISABLE eMMC BOOT', False), 2: ('1-2 DISABLE eMMC BOOT', False),
    3:  ('3-4 WRITE-PROT EEPROM', False), 4: ('3-4 WRITE-PROT EEPROM', False),
    5:  ('UNKNOWN', False), 6:  ('UNKNOWN', False),
    7:  ('UNKNOWN', False), 8:  ('UNKNOWN', False),
    9:  ('UNKNOWN', False), 10: ('UNKNOWN', False),
    11: ('UNKNOWN', False), 12: ('UNKNOWN', False),
    13: ('UNKNOWN', False), 14: ('UNKNOWN', False),
    }

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

