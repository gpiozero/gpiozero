# vim: set fileencoding=utf-8:
#
# GPIO Zero: a library for controlling the Raspberry Pi's GPIO pins
#
# Copyright (c) 2016-2023 Dave Jones <dave@waveform.org.uk>
# Copyright (c) 2019 Ben Nuttall <ben@bennuttall.com>
# Copyright (c) 2017-2018 Andrew Scheller <github@loowis.durge.org>
#
# SPDX-License-Identifier: BSD-3-Clause

# Board layout ASCII art

REV1_BOARD = """\
{style:white on green}+------------------{style:black on white}| |{style:white on green}--{style:on cyan}| |{style:on green}------+{style:reset}
{style:white on green}| {P1:{style} col2}{style:white on green} P1 {style:black on yellow}|C|{style:white on green}{P2:{style} row8}{style:white on green} {style:on cyan}|A|{style:on green}      |{style:reset}
{style:white on green}| {P1:{style} col1}{style:white on green}    {style:black on yellow}+-+{style:white on green}{P2:{style} row7}{P3:{style} row7}{style:white on cyan}+-+{style:on green}      |{style:reset}
{style:white on green}|                     {P2:{style} row6}{P3:{style} row6}{style:white on green}         |{style:reset}
{style:white on green}|               {style:on black}+---+{style:on green} {P2:{style} row5}{P3:{style} row5}{style:on green}        {style:black on white}+===={style:reset}
{style:white on green}|   {style:on black}|D{style:on green}          {style:on black}|SoC|{style:on green} {P2:{style} row4}{P3:{style} row4}{style:on green}        {style:black on white}| USB{style:reset}
{style:white on green}|   {style:on black}|S{style:on green} {style:bold}Pi Model{style:normal} {style:on black}+---+{style:on green} {P2:{style} row3}{P3:{style} row3}{style:on green}        {style:black on white}+===={style:reset}
{style:white on green}|   {style:on black}|I{style:on green} {style:bold}{model:3s}V{pcb_revision:3s}{style:normal}        {P2:{style} row2}{P3:{style} row2}{style:white on green} P3      |{style:reset}
{style:white on green}|   {style:on black}|0{style:on green}             P2 {P2:{style} row1}{P3:{style} row1}{style:white on green}    {style:black on white}+======{style:reset}
{style:white on green}|                        {style:on black}C|{style:on green} {style:black on white}|   Net{style:reset}
{style:white on green}|                        {style:on black}S|{style:on green} {style:black on white}+======{style:reset}
{style:black on white}=pwr{style:white on green}             {style:black on white}|HDMI|{style:white on green}  {style:on black}I|{style:on green}      |{style:reset}
{style:white on green}+----------------{style:black on white}|    |{style:white on green}--{style:on black}0|{style:on green}------+{style:reset}"""

REV2_BOARD = """\
{style:white on green}+------------------{style:black on white}| |{style:white on green}--{style:on cyan}| |{style:on green}------+{style:reset}
{style:white on green}| {P1:{style} col2}{style:white on green} P1 {style:black on yellow}|C|{style:white on green}{P2:{style} row8}{style:white on green} {style:on cyan}|A|{style:on green}      |{style:reset}
{style:white on green}| {P1:{style} col1}{style:white on green}    {style:black on yellow}+-+{style:white on green}{P2:{style} row7}{P3:{style} row7}{style:white on cyan}+-+{style:on green}      |{style:reset}
{style:white on green}|    {P5:{style} col1}{style:white on green}             {P2:{style} row6}{P3:{style} row6}{style:white on green}         |{style:reset}
{style:white on green}| P5 {P5:{style} col2}{style:white on green}       {style:on black}+---+{style:on green} {P2:{style} row5}{P3:{style} row5}{style:on green}        {style:black on white}+===={style:reset}
{style:white on green}|   {style:on black}|D{style:on green}          {style:on black}|SoC|{style:on green} {P2:{style} row4}{P3:{style} row4}{style:on green}        {style:black on white}| USB{style:reset}
{style:white on green}|   {style:on black}|S{style:on green} {style:bold}Pi Model{style:normal} {style:on black}+---+{style:on green} {P2:{style} row3}{P3:{style} row3}{style:on green}        {style:black on white}+===={style:reset}
{style:white on green}|   {style:on black}|I{style:on green} {style:bold}{model:3s}V{pcb_revision:3s}{style:normal}        {P2:{style} row2}{P3:{style} row2}{style:white on green} P3      |{style:reset}
{style:white on green}|   {style:on black}|0{style:on green}             P2 {P2:{style} row1}{P3:{style} row1}{style:white on green}    {style:black on white}+======{style:reset}
{style:white on green}|                        {style:on black}C|{style:on green} {style:black on white}|   Net{style:reset}
{style:white on green}|            {P6:{style} row2}{style:white on green}           {style:on black}S|{style:on green} {style:black on white}+======{style:reset}
{style:black on white}=pwr{style:white on green}      P6 {P6:{style} row1}{style:white on green}   {style:black on white}|HDMI|{style:white on green}  {style:on black}I|{style:on green}      |{style:reset}
{style:white on green}+----------------{style:black on white}|    |{style:white on green}--{style:on black}0|{style:on green}------+{style:reset}"""

A_BOARD = """\
{style:white on green}+------------------{style:black on white}| |{style:white on green}--{style:on cyan}| |{style:on green}------+{style:reset}
{style:white on green}| {P1:{style} col2}{style:white on green} P1 {style:black on yellow}|C|{style:white on green}{P2:{style} row8}{style:white on green} {style:on cyan}|A|{style:on green}      |{style:reset}
{style:white on green}| {P1:{style} col1}{style:white on green}    {style:black on yellow}+-+{style:white on green}{P2:{style} row7}{P3:{style} row7}{style:white on cyan}+-+{style:on green}      |{style:reset}
{style:white on green}|    {P5:{style} col1}{style:white on green}             {P2:{style} row6}{P3:{style} row6}{style:white on green}         |{style:reset}
{style:white on green}| P5 {P5:{style} col2}{style:white on green}       {style:on black}+---+{style:on green} {P2:{style} row5}{P3:{style} row5}{style:on green}        {style:black on white}+===={style:reset}
{style:white on green}|   {style:on black}|D{style:on green}          {style:on black}|SoC|{style:on green} {P2:{style} row4}{P3:{style} row4}{style:on green}        {style:black on white}| USB{style:reset}
{style:white on green}|   {style:on black}|S{style:on green} {style:bold}Pi Model{style:normal} {style:on black}+---+{style:on green} {P2:{style} row3}{P3:{style} row3}{style:on green}        {style:black on white}+===={style:reset}
{style:white on green}|   {style:on black}|I{style:on green} {style:bold}{model:3s}V{pcb_revision:3s}{style:normal}        {P2:{style} row2}{P3:{style} row2}{style:white on green} P3      |{style:reset}
{style:white on green}|   {style:on black}|0{style:on green}             P2 {P2:{style} row1}{P3:{style} row1}{style:white on green}         |{style:reset}
{style:white on green}|                        {style:on black}C|{style:on green}      |{style:reset}
{style:white on green}|            {P6:{style} row2}{style:white on green}           {style:on black}S|{style:on green}      |{style:reset}
{style:black on white}=pwr{style:white on green}      P6 {P6:{style} row1}{style:white on green}   {style:black on white}|HDMI|{style:white on green}  {style:on black}I|{style:on green}      |{style:reset}
{style:white on green}+----------------{style:black on white}|    |{style:white on green}--{style:on black}0|{style:on green}------+{style:reset}"""

BPLUS_BOARD = """\
{style:white on green},--------------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8     {style:black on white}+===={style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}        {style:black on white}| USB{style:reset}
{style:white on green}|                             {style:black on white}+===={style:reset}
{style:white on green}| {RUN:{style} rev col1}{style:white on green} RUN{style:bold}  Pi Model {model:4s}V{pcb_revision:3s}{style:normal}      |{style:reset}
{style:white on green}| {style:on black}|D{style:on green}      {style:on black}+---+{style:on green}               {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|{style:black on white}S{style:white on green}      {style:on black}|SoC|{style:on green}               {style:black on white}| USB{style:reset}
{style:white on green}| {style:on black}|{style:black on white}I{style:white on green}      {style:on black}+---+{style:on green}               {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|0{style:on green}               {style:on black}C|{style:on green}            |{style:reset}
{style:white on green}|                  {style:black on white}S{style:white on black}|{style:on green}       {style:black on white}+======{style:reset}
{style:white on green}|                  {style:black on white}I{style:white on black}|{style:on green} {style:on black}|A|{style:on green}   {style:black on white}|   Net{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}      {style:black on white}|HDMI|{style:white on green}  {style:on black}0|{style:on green} {style:on black}|u|{style:on green}   {style:black on white}+======{style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}------{style:black on white}|    |{style:white on green}-----{style:on black}|x|{style:on green}--------'{style:reset}"""

B3PLUS_BOARD = """\
{style:white on green},--------------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8 PoE {style:black on white}+===={style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}   {POE:{style} row1}{style:on green}   {style:black on white}| USB{style:reset}
{style:white on green}| {style:black on white} Wi {style:white on green}                   {POE:{style} row2}{style:on green}   {style:black on white}+===={style:reset}
{style:white on green}| {style:black on white} Fi {style:white on green} {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal}         |{style:reset}
{style:white on green}| {style:on black}|D{style:on green}     {style:black on white},---.{style:on green}           {RUN:{style} col1}{style:on green}   {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|{style:black on white}S{style:white on green}     {style:black on white}|SoC|{style:white on green}            RUN {style:black on white}| USB{style:reset}
{style:white on green}| {style:on black}|{style:black on white}I{style:white on green}     {style:black on white}`---'{style:on green}                {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|0{style:on green}               {style:on black}C|{style:on green}            |{style:reset}
{style:white on green}|                  {style:black on white}S{style:white on black}|{style:on green}       {style:black on white}+======{style:reset}
{style:white on green}|                  {style:black on white}I{style:white on black}|{style:on green} {style:on black}|A|{style:on green}   {style:black on white}|   Net{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}      {style:black on white}|HDMI|{style:white on green}  {style:on black}0|{style:on green} {style:on black}|u|{style:on green}   {style:black on white}+======{style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}------{style:black on white}|    |{style:white on green}-----{style:on black}|x|{style:on green}--------'{style:reset}"""

B4_BOARD = """\
{style:white on green},--------------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8   {style:black on white}+======{style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}  J14 {style:black on white}|   Net{style:reset}
{style:white on green}| {style:black on white} Wi {style:white on green}                   {J14:{style} row1}{style:on green} {style:black on white}+======{style:reset}
{style:white on green}| {style:black on white} Fi {style:white on green} {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal} {J14:{style} row2}{style:normal white on green}      |{style:reset}
{style:white on green}| {style:on black}|D{style:on green}     {style:black on white},---.{style:on green} {style:white on black}+---+{style:on green}          {style:blue on white}+===={style:reset}
{style:white on green}| {style:on black}|{style:black on white}S{style:white on green}     {style:black on white}|SoC|{style:on green} {style:white on black}|RAM|{style:on green}          {style:blue on white}|USB3{style:reset}
{style:white on green}| {style:on black}|{style:black on white}I{style:white on green}     {style:black on white}`---'{style:on green} {style:white on black}+---+{style:on green}          {style:blue on white}+===={style:reset}
{style:white on green}| {style:on black}|0{style:on green}                {style:on black}C|{style:white on green}           |{style:reset}
{style:white on green}| {J2:{style} rev col1}{style:white on green} J2            {style:black on white}S{style:white on black}|{style:on green}        {style:black on white}+===={style:reset}
{style:white on green}|                   {style:black on white}I{style:white on black}|{style:on green} {style:white on black}|A|{style:white on green}    {style:black on white}|USB2{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}   {style:black on white}|hd|{style:white on green}   {style:black on white}|hd|{style:white on green} {style:on black}0|{style:on green} {style:on black}|u|{style:on green}    {style:black on white}+===={style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}---{style:black on white}|m0|{style:white on green}---{style:black on white}|m1|{style:white on green}----{style:on black}|x|{style:on green}-------'{style:reset}"""

B5_BOARD = """\
{style:white on green},--------------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8   {style:black on white}:{style:on green} {style:on white}+===={style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}      {style:black on white}:{style:on green} {style:on white}|USB2{style:reset}
{style:white on green}| {style:black on white} Wi {style:white on green} {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal}  fan {style:black on white}+===={style:reset}
{style:white on green}| {style:black on white} Fi {style:white on green}    {style:on black}+---+{style:on green}      {style:on black}+---+{style:on green}       |{style:reset}
{style:white on green}|         {style:on black}|RAM|{style:on green}      {style:on black}|RP1|{style:on green}    {style:blue on white}+===={style:reset}
{style:white on green}|{style:black on yellow}|p{style:white on green}       {style:on black}+---+{style:on green}      {style:on black}+---+{style:on green}    {style:blue on white}|USB3{style:reset}
{style:white on green}|{style:black on yellow}|{style:on white}c{style:white on green}      {style:black on white}-------{style:white on green}              {style:blue on white}+===={style:reset}
{style:white on green}|{style:black on yellow}|i{style:white on green}      {style:black on white}  SoC  {style:white on green}    {style:black on yellow}|c|c{style:white on green} J14     |{style:reset}
{style:bold white on green}({style:normal}        {style:black on white}-------{style:white on green}  J7{style:black on yellow}|{style:on white}s{style:on yellow}|{style:on white}s{style:white on green} {J14:{style} row1}{style:on green} {style:black on white}+======{style:reset}
{style:white on green}|  J2 bat   uart   {J7:{style} row1}{style:black on yellow}|{style:on white}i{style:on yellow}|{style:on white}i{style:white on green} {J14:{style} row2}{style:on green} {style:black on white}|   Net{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}\\{style:black on white}..|hd|...|hd|{style:white on green}{J7:{style} row2}{style:black on yellow}|1|0{style:white on green}    {style:black on white}+======{style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}-{J2:{style} col1}{style:black on white}|m0|{style:white on green}---{style:black on white}|m1|{style:white on green}--------------'{style:reset}"""

APLUS_BOARD = """\
{style:white on green},--------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8  |{style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}     |{style:reset}
{style:white on green}|                          |{style:reset}
{style:white on green}|      {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal}   |{style:reset}
{style:white on green}| {style:on black}|D{style:on green}      {style:on black}+---+{style:on green}         {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|S{style:on green}      {style:on black}|SoC|{style:on green}         {style:black on white}| USB{style:reset}
{style:white on green}| {style:on black}|I{style:on green}      {style:on black}+---+{style:on green}         {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|0{style:on green}               {style:on black}C|{style:on green}      |{style:reset}
{style:white on green}|                  {style:on black}S|{style:on green}      |{style:reset}
{style:white on green}|                  {style:on black}I|{style:on green} {style:on black}|A|{style:on green}  |{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}      {style:black on white}|HDMI|{style:white on green}  {style:on black}0|{style:on green} {style:on black}|u|{style:on green}  |{style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}------{style:black on white}|    |{style:white on green}-----{style:on black}|x|{style:on green}--'{style:reset}"""

A3PLUS_BOARD = """\
{style:white on green},--------------------------.{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green} J8  |{style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}  RUN|{style:reset}
{style:white on green}| {style:black on white} Wi {style:white on green}                   {RUN:{style} col1}{style:white on green}|{style:reset}
{style:white on green}| {style:black on white} Fi {style:white on green} {style:bold}Pi Model {model:4s}V{pcb_revision:3s}{style:normal}   |{style:reset}
{style:white on green}| {style:on black}|D{style:on green}     {style:black on white},---.{style:on green}          {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|{style:black on white}S{style:white on green}     {style:black on white}|SoC|{style:on green}          {style:black on white}| USB{style:reset}
{style:white on green}| {style:on black}|{style:black on white}I{style:white on green}     {style:black on white}`---'{style:on green}          {style:black on white}+===={style:reset}
{style:white on green}| {style:on black}|0{style:on green}               {style:on black}C|{style:on green}      |{style:reset}
{style:white on green}|                  {style:black on white}S{style:white on black}|{style:on green}      |{style:reset}
{style:white on green}|                  {style:black on white}I{style:white on black}|{style:on green} {style:on black}|A|{style:on green}  |{style:reset}
{style:white on green}| {style:black on white}pwr{style:white on green}      {style:black on white}|HDMI|{style:white on green}  {style:on black}0|{style:on green} {style:on black}|u|{style:on green}  |{style:reset}
{style:white on green}`-{style:black on white}| |{style:white on green}------{style:black on white}|    |{style:white on green}-----{style:on black}|x|{style:on green}--'{style:reset}"""

ZERO12_BOARD = """\
{style:white on green},--{J8:{style} col2}{style:white on green}---.{style:reset}
{style:white on green}|  {J8:{style} col1}{style:white on green} J8|{style:reset}
{style:black on white}---+{style:white on green} {style:bold}Pi{model:6s}{style:normal}    RUN {RUN:{style} rev col1}{style:white on green}   |{style:reset}
{style:black on white} sd|{style:white on green} {style:bold}V{pcb_revision:3s}{style:normal} {style:white on black}+---+{style:white on green}   TV {TV:{style} col1}{style:white on green}   |{style:reset}
{style:black on white}---+{style:white on green}      {style:white on black}|SoC|{style:white on green}           |{style:reset}
{style:white on green}| {style:black on white}hdmi{style:white on green}    {style:white on black}+---+{style:white on green}   {style:black on white}usb{style:on green} {style:black on white}pwr{style:white on green} |{style:reset}
{style:white on green}`-{style:black on white}|  |{style:white on green}------------{style:black on white}| |{style:white on green}-{style:black on white}| |{style:white on green}-'{style:reset}"""

ZERO13_BOARD = """\
{style:white on green},--{J8:{style} col2}{style:white on green}---.{style:reset}
{style:white on green}|  {J8:{style} col1}{style:white on green} J8|{style:reset}
{style:black on white}---+{style:white on green} {style:bold}Pi{model:6s}{style:normal}    RUN {RUN:{style} rev col1}{style:white on green}   {style:black on white}c{style:white on black}|{style:reset}
{style:black on white} sd|{style:white on green} {style:bold}V{pcb_revision:3s}{style:normal} {style:white on black}+---+{style:white on green}   TV {TV:{style} col1}{style:white on green}   {style:black on white}s{style:white on black}|{style:reset}
{style:black on white}---+{style:white on green}      {style:white on black}|SoC|{style:white on green}           {style:black on white}i{style:white on black}|{style:reset}
{style:white on green}| {style:black on white}hdmi{style:white on green}    {style:white on black}+---+{style:white on green}   {style:black on white}usb{style:on green} {style:black on white}pwr{style:white on green} |{style:reset}
{style:white on green}`-{style:black on white}|  |{style:white on green}------------{style:black on white}| |{style:white on green}-{style:black on white}| |{style:white on green}-'{style:reset}"""

ZERO2_BOARD = """\
{style:white on green},--{J8:{style} col2}{style:white on green}---.{style:reset}
{style:white on green}|  {J8:{style} col1}{style:white on green} J8|{style:reset}
{style:black on white}---+{style:white on green}     {style:normal on black}+---+{style:on green}  {style:bold}Pi{model:6s}  {style:normal black on white}c{style:white on black}|{style:reset}
{style:black on white} sd|{style:white on green}     {style:white on black}|SoC|{style:white on green}  {style:black on white} Wi {style:bold white on green}V{pcb_revision:3s}  {style:normal black on white}s{style:white on black}|{style:reset}
{style:black on white}---+{style:white on green}     {style:white on black}+---+{style:white on green}  {style:black on white} Fi {style:on green}      {style:on white}i{style:white on black}|{style:reset}
{style:white on green}| {style:black on white}hdmi{style:white on green}            {style:black on white}usb{style:on green} {style:black on white}pwr{style:white on green} |{style:reset}
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
{style:white on green}|  {style:black on white}----{style:white on green}   {style:black on white}----{style:white on green}   {style:black on white}----{style:white on green} J2 {J2:{style} col2}{style:bold white on green}|             |{style:normal}{J3:{style} rev col1}{style:white on green}        |{style:reset}
{style:white on green}{style:black on white}c|{style:white on green}    {style:bold}Pi {model:4s} Rev {pcb_revision:3s}{style:normal}    {J2:{style} col1}{style:bold white on green}|       {style:normal black on white} Wi {style:white on green}  {style:bold}|{style:normal}J3         |{style:reset}
{style:white on green}{style:black on white}s|{style:white on green}    {style:bold}IO Board{style:normal}                  {style:bold}|       {style:normal black on white} Fi {style:white on green}  {style:bold}|{style:normal}           |{style:reset}
{style:white on green}{style:black on white}i|{style:white on green}          J6 {J6:{style} col2}{style:bold white on green}               |         {style:normal white on black}+--+{style:on green}{style:bold}|  {style:normal white on black}|P|{style:on green}      |{style:reset}
{style:white on green}| J8           {J6:{style} col1}{style:bold white on green}               |  {style:normal black on white},----.{style:on green} {style:white on black}|eM|{style:bold on green}|  {style:normal white on black}}}-{{{style:on green}      |{style:reset}
{style:white on green}| {J8:{style} col2}{style:white on green}          {style:bold}|  {style:normal black on white}|SoC |{style:on green} {style:white on black}|MC|{style:bold on green}|  {style:normal white on black}|C|{style:on green}      |{style:reset}
{style:white on green}| {J8:{style} col1}{style:white on green}   J9     {style:bold}|  {style:normal black on white}|    |{style:on green} {style:white on black}+--+{style:bold on green}|  {style:normal white on black}|I|{style:on green}      |{style:reset}
{style:white on green}| {style:black on white},---.{style:white on green}                  {J9:{style} row1}{style:bold white on green}     |  {style:normal black on white}`----'{style:white on green}     {style:bold}|  {style:normal white on black}|e|{style:on green}      |{style:reset}
{style:white on green}|{style:black on white}( ={style:on green}O{style:on white} |{style:white on green}                  {J9:{style} row2}{style:bold white on green}     |  {style:normal white on black}+----+{style:on green}     {style:bold}|{style:normal}           |{style:reset}
{style:white on green}| {style:black on white}) + |{style:white on green}                         {style:bold}|  {style:normal white on black}|RAM |{style:bold white on green}     |{style:normal}           |{style:reset}
{style:white on green}|{style:black on white}( ={style:on green}O{style:on white} |{style:white on green}                         {style:bold}`--{style:normal white on black}+----+{style:bold on green}-----'{style:normal}           |{style:reset}
{style:white on green}| {style:black on white}`---'{style:white on green}                                                   |{style:reset}
{style:white on green}|   {J1:{style} rev col1}{style:white on green} J1                                                |{style:reset}
{style:white on green}|                                                         |{style:reset}
{style:white on green}|                          {style:black on white}|Net |{style:on green} {style:black on white}|USB|{style:on green}     {style:black on white}|uSD|{style:white on green}      {style:on black}|p|{style:on green}|{style:reset}
{style:white on green}|    {style:black on white}|HDMI|{style:on green}   {style:black on white}|HDMI|{style:white on green}       {style:black on white}|    |{style:on green} {style:black on white}| 2 |{style:on green} {style:black on white}usb{style:white on green} {style:black on white}|   |{style:white on green}      {style:on black}|w|{style:on green}|{style:reset}
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

# Pin maps for various board revisions and headers. Much of the information
# below is derived from the BCM2835 ARM Peripherals datasheet, but Gadgetoid's
# superb https://pinout.xyz site was also a great deal of help in filling in
# the gaps!

import re
def gpiof(*names):
    return {
        'gpio' if re.match(r'GPIO\d+$', name) else
        'i2c'  if re.match(r'I2C\d (SDA|SCL)$', name) else
        'spi'  if re.match(r'SPI\d (SCLK|MOSI|MISO|CE\d)$', name) else
        'uart' if re.match(r'UART\d (RXD|TXD|RTS|CTS)$', name) else
        'smi'  if re.match(r'SMI (name[AD]\d+|SOE / SE|SWE / SRW)$', name) else
        'dpi'  if re.match(r'DPI (D\d+|PCLK|DE|[HV]SYNC)$', name) else
        'pwm'  if re.match(r'PWM\d+ \d+$', name) else
        'pcm'  if re.match(r'PCM (CLK|FS|DIN|DOUT)$', name) else
        'sdio' if re.match(r'SD\d+ (CLK|CMD|DAT\d+)$', name) else
        'jtag' if re.match(r'JTAG (TDI|TDO|TCK|TMS|RTCK|TRST)$', name) else
        'mii'  if re.match(r'(RG)?MII ', name) else
        '': name
        for name in names
        if name
    }

V1_8 = {'': '1V8'}
V3_3 = {'': '3V3'}
V5   = {'': '5V'}
GND  = {'': 'GND'}
NC   = {'': 'NC'}  # not connected

#                   gpio      alt0         alt1             alt2         alt3              alt4         alt5
PI1_GPIO0  = gpiof('GPIO0',  'I2C0 SDA',  'SMI SA5',       'DPI PCLK')
PI1_GPIO1  = gpiof('GPIO1',  'I2C0 SCL',  'SMI SA4',       'DPI DE')
PI1_GPIO2  = gpiof('GPIO2',  'I2C1 SDA',  'SMI SA3',       'DPI VSYNC')
PI1_GPIO3  = gpiof('GPIO3',  'I2C1 SCL',  'SMI SA2',       'DPI HSYNC')
PI1_GPIO4  = gpiof('GPIO4',  'GPCLK0',    'SMI SA1',       'DPI D0',    '',               '',          'JTAG TDI')
PI1_GPIO5  = gpiof('GPIO5',  'GPCLK1',    'SMI SA0',       'DPI D1',    '',               '',          'JTAG TDO')
PI1_GPIO6  = gpiof('GPIO6',  'GPCLK2',    'SMI SOE / SE',  'DPI D2',    '',               '',          'JTAG RTCK')
PI1_GPIO7  = gpiof('GPIO7',  'SPI0 CE1',  'SMI SWE / SRW', 'DPI D3')
PI1_GPIO8  = gpiof('GPIO8',  'SPI0 CE0',  'SMI SD0',       'DPI D4')
PI1_GPIO9  = gpiof('GPIO9',  'SPI0 MISO', 'SMI SD1',       'DPI D5')
PI1_GPIO10 = gpiof('GPIO10', 'SPI0 MOSI', 'SMI SD2',       'DPI D6')
PI1_GPIO11 = gpiof('GPIO11', 'SPI0 SCLK', 'SMI SD3',       'DPI D7')
PI1_GPIO12 = gpiof('GPIO12', 'PWM0 0',    'SMI SD4',       'DPI D8',    '',               '',          'JTAG TMS' )
PI1_GPIO13 = gpiof('GPIO13', 'PWM0 1',    'SMI SD5',       'DPI D9',    '',               '',          'JTAG TCK' )
PI1_GPIO14 = gpiof('GPIO14', 'UART0 TXD', 'SMI SD6',       'DPI D10'    '',               '',          'UART1 TXD')
PI1_GPIO15 = gpiof('GPIO15', 'UART0 RXD', 'SMI SD7',       'DPI D11'    '',               '',          'UART1 RXD')
PI1_GPIO16 = gpiof('GPIO16', '',          'SMI SD8',       'DPI D11',   'UART0 CTS',      'SPI1 CE2',  'UART1 CTS')
PI1_GPIO17 = gpiof('GPIO17', '',          'SMI SD9',       'DPI D13',   'UART0 RTS',      'SPI1 CE1',  'UART1 RTS')
PI1_GPIO18 = gpiof('GPIO18', 'PCM CLK',   'SMI SD10',      'DPI D14',   'BSC SDA / MOSI', 'SPI1 CE0',  'PWM0 0')
PI1_GPIO19 = gpiof('GPIO19', 'PCM FS',    'SMI SD11',      'DPI D15',   'BSC SCL / SCLK', 'SPI1 MISO', 'PWM0 1')
PI1_GPIO20 = gpiof('GPIO20', 'PCM DIN',   'SMI SD12',      'DPI D16',   'BSC MISO',       'SPI1 MOSI', 'GPCLK0')
PI1_GPIO21 = gpiof('GPIO21', 'PCM DOUT',  'SMI SD13',      'DPI D17',   'BSC CE',         'SPI1 SCLK', 'GPCLK1')
PI1_GPIO22 = gpiof('GPIO22', 'SD0 CLK',   'SMI SD14',      'DPI D18',   'SD1 CLK',        'JTAG TRST')
PI1_GPIO23 = gpiof('GPIO23', 'SD0 CMD',   'SMI SD15',      'DPI D19',   'SD1 CMD',        'JTAG RTCK')
PI1_GPIO24 = gpiof('GPIO24', 'SD0 DAT0',  'SMI SD16',      'DPI D20',   'SD1 DAT0',       'JTAG TDO')
PI1_GPIO25 = gpiof('GPIO25', 'SD0 DAT1',  'SMI SD17',      'DPI D21',   'SD1 DAT1',       'JTAG TCK')
PI1_GPIO26 = gpiof('GPIO26', 'SD0 DAT2',  '',              'DPI D22',   'SD1 DAT2',       'JTAG TDI')
PI1_GPIO27 = gpiof('GPIO27', 'SD0 DAT3',  '',              'DPI D23',   'SD1 DAT3',       'JTAG TMS')
PI1_GPIO28 = gpiof('GPIO28', 'I2C0 SDA',  'SMI SA5',       'PCM CLK')
PI1_GPIO29 = gpiof('GPIO29', 'I2C0 SCL',  'SMI SA4',       'PCM FS')
PI1_GPIO30 = gpiof('GPIO30', '',          'SMI SA3',       'PCM DIN',   'UART0 CTS',      '',          'UART1 CTS')
PI1_GPIO31 = gpiof('GPIO31', '',          'SMI SA2',       'PCM DOUT',  'UART0 RTS',      '',          'UART1 RTS')
PI1_GPIO32 = gpiof('GPIO32', 'GPCLK0',    'SMI SA1',       '',          'UART0 TXD',      '',          'UART1 TXD')
PI1_GPIO33 = gpiof('GPIO33', '',          'SMI SA0',       '',          'UART0 RXD',      '',          'UART1 RXD')
PI1_GPIO34 = gpiof('GPIO34', 'GPCLK0',    'SMI SOE / SE')
PI1_GPIO35 = gpiof('GPIO35', 'SPI0 CE1',  'SMI SWE / SRW')
PI1_GPIO36 = gpiof('GPIO36', 'SPI0 CE0',  'SMI SD0',       'UART0 TXD')
PI1_GPIO37 = gpiof('GPIO37', 'SPI0 MISO', 'SMI SD1',       'UART0 RXD')
PI1_GPIO38 = gpiof('GPIO38', 'SPI0 MOSI', 'SMI SD2',       'UART0 RTS')
PI1_GPIO39 = gpiof('GPIO39', 'SPI0 SCLK', 'SMI SD3',       'UART0 CTS')
PI1_GPIO40 = gpiof('GPIO40', 'PWM0 0',    'SMI SD4',       '',          '',               'SPI2 MISO', 'UART1 TXD')
PI1_GPIO41 = gpiof('GPIO41', 'PWM0 1',    'SMI SD5',       '',          '',               'SPI2 MOSI', 'UART1 RXD')
PI1_GPIO42 = gpiof('GPIO42', 'GPCLK1',    'SMI SD6',       '',          '',               'SPI2 SCLK', 'UART1 RTS')
PI1_GPIO43 = gpiof('GPIO43', 'GPCLK2',    'SMI SD7',       '',          '',               'SPI2 CE0',  'UART1 CTS')
PI1_GPIO44 = gpiof('GPIO44', 'GPCLK1',    'I2C0 SDA',      'I2C1 SDA',  '',               'SPI2 CE1')
PI1_GPIO45 = gpiof('GPIO45', 'PWM0 1',    'I2C0 SCL',      'I2C1 SCL',  '',               'SPI2 CE2')
PI1_GPIO46 = gpiof('GPIO46')
PI1_GPIO47 = gpiof('GPIO47')
PI1_GPIO48 = gpiof('GPIO48')
PI1_GPIO49 = gpiof('GPIO49')
PI1_GPIO50 = gpiof('GPIO50')
PI1_GPIO51 = gpiof('GPIO51')
PI1_GPIO52 = gpiof('GPIO52')
PI1_GPIO53 = gpiof('GPIO53')

#                   gpio      alt0         alt1             alt2         alt3              alt4                alt5
PI4_GPIO0  = gpiof('GPIO0',  'I2C0 SDA',  'SMI SA5',       'DPI PCLK',  'SPI3 CE0',       'UART2 TXD',        'I2C6 SDA')
PI4_GPIO1  = gpiof('GPIO1',  'I2C0 SCL',  'SMI SA4',       'DPI DE',    'SPI3 MISO',      'UART2 RXD',        'I2C6 SCL')
PI4_GPIO2  = gpiof('GPIO2',  'I2C1 SDA',  'SMI SA3',       'DPI VSYNC', 'SPI3 MOSI',      'UART2 CTS',        'I2C3 SDA')
PI4_GPIO3  = gpiof('GPIO3',  'I2C1 SCL',  'SMI SA2',       'DPI HSYNC', 'SPI3 SCLK',      'UART2 RTS',        'I2C3 SCL')
PI4_GPIO4  = gpiof('GPIO4',  'GPCLK0',    'SMI SA1',       'DPI D0',    'SPI4 CE0',       'UART3 TXD',        'I2C3 SDA')
PI4_GPIO5  = gpiof('GPIO5',  'GPCLK1',    'SMI SA0',       'DPI D1',    'SPI4 MISO',      'UART3 RXD',        'I2C3 SCL')
PI4_GPIO6  = gpiof('GPIO6',  'GPCLK2',    'SMI SOE / SE',  'DPI D2',    'SPI4 MOSI',      'UART3 CTS',        'I2C4 SDA')
PI4_GPIO7  = gpiof('GPIO7',  'SPI0 CE1',  'SMI SWE / SRW', 'DPI D3',    'SPI4 SCLK',      'UART3 RTS',        'I2C4 SCL')
PI4_GPIO8  = gpiof('GPIO8',  'SPI0 CE0',  'SMI SD0',       'DPI D4',    'BSC CE',         'UART4 TXD',        'I2C4 SDA')
PI4_GPIO9  = gpiof('GPIO9',  'SPI0 MISO', 'SMI SD1',       'DPI D5',    'BSC MISO',       'UART4 RXD',        'I2C4 SCL')
PI4_GPIO10 = gpiof('GPIO10', 'SPI0 MOSI', 'SMI SD2',       'DPI D6',    'BSC SDA / MOSI', 'UART4 CTS',        'I2C5 SDA')
PI4_GPIO11 = gpiof('GPIO11', 'SPI0 SCLK', 'SMI SD3',       'DPI D7',    'BSC SCL / SCLK', 'UART4 RTS',        'I2C5 SCL')
PI4_GPIO12 = gpiof('GPIO12', 'PWM0 0',    'SMI SD4',       'DPI D8',    'SPI5 CE0',       'UART5 TXD',        'I2C5 SDA')
PI4_GPIO13 = gpiof('GPIO13', 'PWM0 1',    'SMI SD5',       'DPI D9',    'SPI5 MISO',      'UART5 RXD',        'I2C5 SCL')
PI4_GPIO14 = gpiof('GPIO14', 'UART0 TXD', 'SMI SD6',       'DPI D10',   'SPI5 MOSI',      'UART5 CTS',        'UART1 TXD')
PI4_GPIO15 = gpiof('GPIO15', 'UART0 RXD', 'SMI SD7',       'DPI D11',   'SPI5 SCLK',      'UART5 RTS',        'UART1 RXD')
PI4_GPIO16 = gpiof('GPIO16', '',          'SMI SD8',       'DPI D12',   'UART0 CTS',      'SPI1 CE2',         'UART1 CTS')
PI4_GPIO17 = gpiof('GPIO17', '',          'SMI SD9',       'DPI D13',   'UART0 RTS',      'SPI1 CE1',         'UART1 RTS')
PI4_GPIO18 = gpiof('GPIO18', 'PCM CLK',   'SMI SD10',      'DPI D14',   'SPI6 CE0',       'SPI1 CE0',         'PWM0 0')
PI4_GPIO19 = gpiof('GPIO19', 'PCM FS',    'SMI SD11',      'DPI D15',   'SPI6 MISO',      'SPI1 MISO',        'PWM0 1')
PI4_GPIO20 = gpiof('GPIO20', 'PCM DIN',   'SMI SD12',      'DPI D16',   'SPI6 MOSI',      'SPI1 MOSI',        'GPCLK0')
PI4_GPIO21 = gpiof('GPIO21', 'PCM DOUT',  'SMI SD13',      'DPI D17',   'SPI6 SCLK',      'SPI1 SCLK',        'GPCLK1')
PI4_GPIO22 = gpiof('GPIO22', 'SD0 CLK',   'SMI SD14',      'DPI D18',   'SD1 CLK',        'JTAG TRST',        'I2C6 SDA')
PI4_GPIO23 = gpiof('GPIO23', 'SD0 CMD',   'SMI SD15',      'DPI D19',   'SD1 CMD',        'JTAG RTCK',        'I2C6 SCL')
PI4_GPIO24 = gpiof('GPIO24', 'SD0 DAT0',  'SMI SD16',      'DPI D20',   'SD1 DAT0',       'JTAG TDO',         'SPI3 CE1')
PI4_GPIO25 = gpiof('GPIO25', 'SD0 DAT1',  'SMI SD17',      'DPI D21',   'SD1 DAT1',       'JTAG TCK',         'SPI4 CE1')
PI4_GPIO26 = gpiof('GPIO26', 'SDA DAT2',  '',              'DPI D22',   'SD1 DAT2',       'JTAG TDI',         'SPI5 CE1')
PI4_GPIO27 = gpiof('GPIO27', 'SDA DAT3',  '',              'DPI D23',   'SD1 DAT3',       'JTAG TMS',         'SPI6 CE1')
PI4_GPIO28 = gpiof('GPIO28', 'I2C0 SDA',  'SMI SA5',       'PCM CLK',   '',               'MII RX ERR',       'RGMII MDIO')
PI4_GPIO29 = gpiof('GPIO29', 'I2C0 SCL',  'SMI SA4',       'PCM FS',    '',               'MII TX ERR',       'RGMII MDC')
PI4_GPIO30 = gpiof('GPIO30', '',          'SMI SA3',       'PCM DIN',   'UART0 CTS',      'MII CRS',          'UART1 CTS')
PI4_GPIO31 = gpiof('GPIO31', '',          'SMI SA2',       'PCM DOUT',  'UART0 RTS',      'MII COL',          'UART1 RTS')
PI4_GPIO32 = gpiof('GPIO32', 'GPCLK0',    'SMI SA1',       '',          'UART0 TXD',      'SD CARD PRES',     'UART1 TXD')
PI4_GPIO33 = gpiof('GPIO33', '',          'SMI SA0',       '',          'UART0 RXD',      'SD CARD WRPROT',   'UART1 RXD')
PI4_GPIO34 = gpiof('GPIO34', 'GPCLK0',    'SMI SOE / SE',  '',          'SD1 CLK',        'SD CARD LED',      'RGMII IRQ')
PI4_GPIO35 = gpiof('GPIO35', 'SPI0 CE1',  'SMI SWE / SRW', '',          'SD1 CMD',        'RGMII START STOP')
PI4_GPIO36 = gpiof('GPIO36', 'SPI0 CE0',  'SMI SD0',       'UART0 TXD', 'SD1 DAT0',       'RGMII RX OK',      'MII RX ERR')
PI4_GPIO37 = gpiof('GPIO37', 'SPI0 MISO', 'SMI SD1',       'UART0 RXD', 'SD1 DAT1',       'RGMII MDIO',       'MII TX ERR')
PI4_GPIO38 = gpiof('GPIO38', 'SPI0 MOSI', 'SMI SD2',       'UART0 RTS', 'SD1 DAT2',       'RGMII MDC',        'MII CRS')
PI4_GPIO39 = gpiof('GPIO39', 'SPI0 SCLK', 'SMI SD3',       'UART0 CTS', 'SD1 DAT3',       'RGMII IRQ',        'MII COL')
PI4_GPIO40 = gpiof('GPIO40', 'PWM1 0',    'SMI SD4',       '',          'SD1 DAT4',       'SPI0 MISO',        'UART1 TXD')
PI4_GPIO41 = gpiof('GPIO41', 'PWM1 1',    'SMI SD5',       '',          'SD1 DAT5',       'SPI0 MOSI',        'UART1 RXD')
PI4_GPIO42 = gpiof('GPIO42', 'GPCLK1',    'SMI SD6',       '',          'SD1 DAT6',       'SPI0 SCLK',        'UART1 RTS')
PI4_GPIO43 = gpiof('GPIO43', 'GPCLK2',    'SMI SD7',       '',          'SD1 DAT7',       'SPI0 CE0',         'UART1 CTS')
PI4_GPIO44 = gpiof('GPIO44', 'GPCLK1',    'I2C0 SDA',      'I2C1 SDA',  '',               'SPI0 CE1',         'SD CARD VOLT')
PI4_GPIO45 = gpiof('GPIO45', 'PWM0 1',    'I2C0 SCL',      'I2C1 SCL',  '',               'SPI0 CE2',         'SD CARD PWR0')
PI4_GPIO46 = gpiof('GPIO46')
PI4_GPIO47 = gpiof('GPIO47')
PI4_GPIO48 = gpiof('GPIO48')
PI4_GPIO49 = gpiof('GPIO49')
PI4_GPIO50 = gpiof('GPIO50')
PI4_GPIO51 = gpiof('GPIO51')
PI4_GPIO52 = gpiof('GPIO52')
PI4_GPIO53 = gpiof('GPIO53')
PI4_GPIO54 = gpiof('GPIO54')
PI4_GPIO55 = gpiof('GPIO55')
PI4_GPIO56 = gpiof('GPIO56')
PI4_GPIO57 = gpiof('GPIO57')

del gpiof
del re

REV1_P1 = (13, 2, {
    1:  V3_3,       2:  V5,
    3:  PI1_GPIO0,  4:  V5,
    5:  PI1_GPIO1,  6:  GND,
    7:  PI1_GPIO4,  8:  PI1_GPIO14,
    9:  GND,        10: PI1_GPIO15,
    11: PI1_GPIO17, 12: PI1_GPIO18,
    13: PI1_GPIO21, 14: GND,
    15: PI1_GPIO22, 16: PI1_GPIO23,
    17: V3_3,       18: PI1_GPIO24,
    19: PI1_GPIO10, 20: GND,
    21: PI1_GPIO9,  22: PI1_GPIO25,
    23: PI1_GPIO11, 24: PI1_GPIO8,
    25: GND,        26: PI1_GPIO7,
})

REV2_P1 = (13, 2, {
    1:  V3_3,       2:  V5,
    3:  PI1_GPIO2,  4:  V5,
    5:  PI1_GPIO3,  6:  GND,
    7:  PI1_GPIO4,  8:  PI1_GPIO14,
    9:  GND,        10: PI1_GPIO15,
    11: PI1_GPIO17, 12: PI1_GPIO18,
    13: PI1_GPIO27, 14: GND,
    15: PI1_GPIO22, 16: PI1_GPIO23,
    17: V3_3,       18: PI1_GPIO24,
    19: PI1_GPIO10, 20: GND,
    21: PI1_GPIO9,  22: PI1_GPIO25,
    23: PI1_GPIO11, 24: PI1_GPIO8,
    25: GND,        26: PI1_GPIO7,
})

REV2_P5 = (4, 2, {
    1:  V5,         2: V3_3,
    3:  PI1_GPIO28, 4: PI1_GPIO29,
    5:  PI1_GPIO30, 6: PI1_GPIO31,
    7:  GND,        8: GND,
})

PI1_P2 = (8, 1, {
    1: {'': 'GPU JTAG'},
    2: {'': 'GPU JTAG'},
    3: {'': 'GPU JTAG'},
    4: {'': 'GPU JTAG'},
    5: {'': 'GPU JTAG'},
    6: {'': 'GPU JTAG'},
    7: {'': 'GPU JTAG'},
    8: {'': 'GPU JTAG'},
})

PI1_P3 = (7, 1, {
    1: {'': 'LAN JTAG'},
    2: {'': 'LAN JTAG'},
    3: {'': 'LAN JTAG'},
    4: {'': 'LAN JTAG'},
    5: {'': 'LAN JTAG'},
    6: {'': 'LAN JTAG'},
    7: {'': 'LAN JTAG'},
})

REV2_P6 = (2, 1, {
    1: {'': 'RUN'},
    2: GND,
})

PLUS_J8 = (20, 2, {
    1:  V3_3,       2:  V5,
    3:  PI1_GPIO2,  4:  V5,
    5:  PI1_GPIO3,  6:  GND,
    7:  PI1_GPIO4,  8:  PI1_GPIO14,
    9:  GND,        10: PI1_GPIO15,
    11: PI1_GPIO17, 12: PI1_GPIO18,
    13: PI1_GPIO27, 14: GND,
    15: PI1_GPIO22, 16: PI1_GPIO23,
    17: V3_3,       18: PI1_GPIO24,
    19: PI1_GPIO10, 20: GND,
    21: PI1_GPIO9,  22: PI1_GPIO25,
    23: PI1_GPIO11, 24: PI1_GPIO8,
    25: GND,        26: PI1_GPIO7,
    27: PI1_GPIO0,  28: PI1_GPIO1,
    29: PI1_GPIO5,  30: GND,
    31: PI1_GPIO6,  32: PI1_GPIO12,
    33: PI1_GPIO13, 34: GND,
    35: PI1_GPIO19, 36: PI1_GPIO16,
    37: PI1_GPIO26, 38: PI1_GPIO20,
    39: GND,        40: PI1_GPIO21,
})

PLUS_POE = (2, 2, {
    1: {'': 'TR01 TAP'}, 2: {'': 'TR00 TAP'},
    3: {'': 'TR03 TAP'}, 4: {'': 'TR02 TAP'},
})

PLUS_RUN = (2, 1, {
    1: {'': 'POWER ENABLE'},
    2: {'': 'RUN'},
})

ZERO_RUN = REV2_P6

ZERO_TV = (2, 1, {
    1: {'': 'COMPOSITE'},
    2: GND,
})

PI4_J8 = (20, 2, {
    1:  V3_3,       2:  V5,
    3:  PI4_GPIO2,  4:  V5,
    5:  PI4_GPIO3,  6:  GND,
    7:  PI4_GPIO4,  8:  PI4_GPIO14,
    9:  GND,        10: PI4_GPIO15,
    11: PI4_GPIO17, 12: PI4_GPIO18,
    13: PI4_GPIO27, 14: GND,
    15: PI4_GPIO22, 16: PI4_GPIO23,
    17: V3_3,       18: PI4_GPIO24,
    19: PI4_GPIO10, 20: GND,
    21: PI4_GPIO9,  22: PI4_GPIO25,
    23: PI4_GPIO11, 24: PI4_GPIO8,
    25: GND,        26: PI4_GPIO7,
    27: PI4_GPIO0,  28: PI4_GPIO1,
    29: PI4_GPIO5,  30: GND,
    31: PI4_GPIO6,  32: PI4_GPIO12,
    33: PI4_GPIO13, 34: GND,
    35: PI4_GPIO19, 36: PI4_GPIO16,
    37: PI4_GPIO26, 38: PI4_GPIO20,
    39: GND,        40: PI4_GPIO21,
})

PI4_J2 = (3, 1, {
    1: {'': 'GLOBAL ENABLE'},
    2: GND,
    3: {'': 'RUN'},
})

PI4_J14 = PLUS_POE

PI5_J2 = (2, 1, {
    1: {'': 'RUN'},
    2: GND,
})

PI5_J7 = (2, 1, {
    1: {'': 'COMPOSITE'},
    2: GND,
})

CM_SODIMM = (100, 2, {
    1:   GND,                    2:   {'': 'EMMC DISABLE N'},
    3:   PI1_GPIO0,              4:   NC,
    5:   PI1_GPIO1,              6:   NC,
    7:   GND,                    8:   NC,
    9:   PI1_GPIO2,              10:  NC,
    11:  PI1_GPIO3,              12:  NC,
    13:  GND,                    14:  NC,
    15:  PI1_GPIO4,              16:  NC,
    17:  PI1_GPIO5,              18:  NC,
    19:  GND,                    20:  NC,
    21:  PI1_GPIO6,              22:  NC,
    23:  PI1_GPIO7,              24:  NC,
    25:  GND,                    26:  GND,
    27:  PI1_GPIO8,              28:  PI1_GPIO28,
    29:  PI1_GPIO9,              30:  PI1_GPIO29,
    31:  GND,                    32:  GND,
    33:  PI1_GPIO10,             34:  PI1_GPIO30,
    35:  PI1_GPIO11,             36:  PI1_GPIO31,
    37:  GND,                    38:  GND,
    39:  {'': 'GPIO0-27 VREF'},  40:  {'': 'GPIO0-27 VREF'},
    # Gap in SODIMM pins
    41:  {'': 'GPIO28-45 VREF'}, 42:  {'': 'GPIO28-45 VREF'},
    43:  GND,                    44:  GND,
    45:  PI1_GPIO12,             46:  PI1_GPIO32,
    47:  PI1_GPIO13,             48:  PI1_GPIO33,
    49:  GND,                    50:  GND,
    51:  PI1_GPIO14,             52:  PI1_GPIO34,
    53:  PI1_GPIO15,             54:  PI1_GPIO35,
    55:  GND,                    56:  GND,
    57:  PI1_GPIO16,             58:  PI1_GPIO36,
    59:  PI1_GPIO17,             60:  PI1_GPIO37,
    61:  GND,                    62:  GND,
    63:  PI1_GPIO18,             64:  PI1_GPIO38,
    65:  PI1_GPIO19,             66:  PI1_GPIO39,
    67:  GND,                    68:  GND,
    69:  PI1_GPIO20,             70:  PI1_GPIO40,
    71:  PI1_GPIO21,             72:  PI1_GPIO41,
    73:  GND,                    74:  GND,
    75:  PI1_GPIO22,             76:  PI1_GPIO42,
    77:  PI1_GPIO23,             78:  PI1_GPIO43,
    79:  GND,                    80:  GND,
    81:  PI1_GPIO24,             82:  PI1_GPIO44,
    83:  PI1_GPIO25,             84:  PI1_GPIO45,
    85:  GND,                    86:  GND,
    87:  PI1_GPIO26,             88:  {'': 'GPIO46 1V8'},
    89:  PI1_GPIO27,             90:  {'': 'GPIO47 1V8'},
    91:  GND,                    92:  GND,
    93:  {'': 'DSI0 DN1'},       94:  {'': 'DSI1 DP0'},
    95:  {'': 'DSI0 DP1'},       96:  {'': 'DSI1 DN0'},
    97:  GND,                    98:  GND,
    99:  {'': 'DSI0 DN0'},       100: {'': 'DSI1 CP'},
    101: {'': 'DSI0 DP0'},       102: {'': 'DSI1 CN'},
    103: GND,                    104: GND,
    105: {'': 'DSI0 CN'},        106: {'': 'DSI1 DP3'},
    107: {'': 'DSI0 CP'},        108: {'': 'DSI1 DN3'},
    109: GND,                    110: GND,
    111: {'': 'HDMI CK N'},      112: {'': 'DSI1 DP2'},
    113: {'': 'HDMI CK P'},      114: {'': 'DSI1 DN2'},
    115: GND,                    116: GND,
    117: {'': 'HDMI D0 N'},      118: {'': 'DSI1 DP1'},
    119: {'': 'HDMI D0 P'},      120: {'': 'DSI1 DN1'},
    121: GND,                    122: GND,
    123: {'': 'HDMI D1 N'},      124: NC,
    125: {'': 'HDMI D1 P'},      126: NC,
    127: GND,                    128: NC,
    129: {'': 'HDMI D2 N'},      130: NC,
    131: {'': 'HDMI D2 P'},      132: NC,
    133: GND,                    134: GND,
    135: {'': 'CAM1 DP3'},       136: {'': 'CAM0 DP0'},
    137: {'': 'CAM1 DN3'},       138: {'': 'CAM0 DN0'},
    139: GND,                    140: GND,
    141: {'': 'CAM1 DP2'},       142: {'': 'CAM0 CP'},
    143: {'': 'CAM1 DN2'},       144: {'': 'CAM0 CN'},
    145: GND,                    146: GND,
    147: {'': 'CAM1 CP'},        148: {'': 'CAM0 DP1'},
    149: {'': 'CAM1 CN'},        150: {'': 'CAM0 DN1'},
    151: GND,                    152: GND,
    153: {'': 'CAM1 DP1'},       154: NC,
    155: {'': 'CAM1 DN1'},       156: NC,
    157: GND,                    158: NC,
    159: {'': 'CAM1 DP0'},       160: NC,
    161: {'': 'CAM1 DN0'},       162: NC,
    163: GND,                    164: GND,
    165: {'': 'USB DP'},         166: {'': 'TVDAC'},
    167: {'': 'USB DM'},         168: {'': 'USB OTGID'},
    169: GND,                    170: GND,
    171: {'': 'HDMI CEC'},       172: {'': 'VC TRST N'},
    173: {'': 'HDMI SDA'},       174: {'': 'VC TDI'},
    175: {'': 'HDMI SCL'},       176: {'': 'VC TMS'},
    177: {'': 'RUN'},            178: {'': 'VC TDO'},
    179: {'': 'VDD CORE'},       180: {'': 'VC TCK'},
    181: GND,                    182: GND,
    183: V1_8,                   184: V1_8,
    185: V1_8,                   186: V1_8,
    187: GND,                    188: GND,
    189: {'': 'VDAC'},           190: {'': 'VDAC'},
    191: V3_3,                   192: V3_3,
    193: V3_3,                   194: V3_3,
    195: GND,                    196: GND,
    197: {'': 'VBAT'},           198: {'': 'VBAT'},
    199: {'': 'VBAT'},           200: {'': 'VBAT'},
})

CM3_SODIMM = (CM_SODIMM[0], CM_SODIMM[1], CM_SODIMM[2].copy())
CM3_SODIMM[-1].update({
    4:  {'': 'NC / SDX VREF'},
    6:  {'': 'NC / SDX VREF'},
    8:  GND,
    10: {'': 'NC / SDX CLK'},
    12: {'': 'NC / SDX CMD'},
    14: GND,
    16: {'': 'NC / SDX D0'},
    18: {'': 'NC / SDX D1'},
    20: GND,
    22: {'': 'NC / SDX D2'},
    24: {'': 'NC / SDX D3'},
    88: {'': 'HDMI HPD N 1V8'},
    90: {'': 'EMMC EN N 1V8'},
})

CM4_J6 = (2, 2, {
    1: {'': '1-2 CAM0+DISP0'}, 2: {'': '1-2 CAM0+DISP0'},
    3: {'': '3-4 CAM0+DISP0'}, 4: {'': '3-4 CAM0+DISP0'},
})

CM4_J2 = (7, 2, {
    1:  {'': '1-2 DISABLE eMMC BOOT'}, 2:  {'': '1-2 DISABLE eMMC BOOT'},
    3:  {'': '3-4 WRITE-PROT EEPROM'}, 4:  {'': '3-4 WRITE-PROT EEPROM'},
    5:  {'': 'AIN0 MXL7704'},          6:  {'': 'AIN1 MXL7704'},
    7:  GND,                           8:  {'': 'SYNC_IN'},
    9:  {'': 'SYNC OUT'},              10: GND,
    11: {'': 'TV OUT'},                12: GND,
    13: {'': '13-14 WAKE'},            14: {'': '13-14 WAKE'},
})

CM4_J1 = PI4_J2
CM4_J9 = PLUS_POE

CM4_J3 = (3, 1, {
    1: {'': 'WL DISABLE'},
    2: GND,
    3: {'': 'BT DISABLE'},
})

# The following data is sourced from a combination of the following locations:
#
# http://elinux.org/RPi_HardwareHistory
# http://elinux.org/RPi_Low-level_peripherals
# https://git.drogon.net/?p=wiringPi;a=blob;f=wiringPi/wiringPi.c#l807
# https://www.raspberrypi.org/documentation/hardware/raspberrypi/revision-codes/README.md

PI_REVISIONS = {
    # rev     model    pcb_rev released soc        manufacturer ram   storage    usb eth wifi   bt     csi dsi headers                         board
    0x2:      ('B',    '1.0', '2012Q1', 'BCM2835', 'Egoman',    256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV1_P1, 'P2': PI1_P2, 'P3': PI1_P3},                               REV1_BOARD,   ),
    0x3:      ('B',    '1.0', '2012Q3', 'BCM2835', 'Egoman',    256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV1_P1, 'P2': PI1_P2, 'P3': PI1_P3},                               REV1_BOARD,   ),
    0x4:      ('B',    '2.0', '2012Q3', 'BCM2835', 'Sony',      256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P2': PI1_P2, 'P3': PI1_P3, 'P5': REV2_P5, 'P6': REV2_P6}, REV2_BOARD,   ),
    0x5:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Qisda',     256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P2': PI1_P2, 'P3': PI1_P3, 'P5': REV2_P5, 'P6': REV2_P6}, REV2_BOARD,   ),
    0x6:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Egoman',    256,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P2': PI1_P2, 'P3': PI1_P3, 'P5': REV2_P5, 'P6': REV2_P6}, REV2_BOARD,   ),
    0x7:      ('A',    '2.0', '2013Q1', 'BCM2835', 'Egoman',    256,  'SD',      1,  0,  False, False, 1,  1,  {'P1': REV2_P1, 'P2': PI1_P2, 'P3': PI1_P3, 'P5': REV2_P5, 'P6': REV2_P6}, A_BOARD,      ),
    0x8:      ('A',    '2.0', '2013Q1', 'BCM2835', 'Sony',      256,  'SD',      1,  0,  False, False, 1,  1,  {'P1': REV2_P1, 'P2': PI1_P2, 'P3': PI1_P3, 'P5': REV2_P5, 'P6': REV2_P6}, A_BOARD,      ),
    0x9:      ('A',    '2.0', '2013Q1', 'BCM2835', 'Qisda',     256,  'SD',      1,  0,  False, False, 1,  1,  {'P1': REV2_P1, 'P2': PI1_P2, 'P3': PI1_P3, 'P5': REV2_P5, 'P6': REV2_P6}, A_BOARD,      ),
    0xd:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Egoman',    512,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P2': PI1_P2, 'P3': PI1_P3, 'P5': REV2_P5, 'P6': REV2_P6}, REV2_BOARD,   ),
    0xe:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Sony',      512,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P2': PI1_P2, 'P3': PI1_P3, 'P5': REV2_P5, 'P6': REV2_P6}, REV2_BOARD,   ),
    0xf:      ('B',    '2.0', '2012Q4', 'BCM2835', 'Qisda',     512,  'SD',      2,  1,  False, False, 1,  1,  {'P1': REV2_P1, 'P2': PI1_P2, 'P3': PI1_P3, 'P5': REV2_P5, 'P6': REV2_P6}, REV2_BOARD,   ),
    0x10:     ('B+',   '1.2', '2014Q3', 'BCM2835', 'Sony',      512,  'MicroSD', 4,  1,  False, False, 1,  1,  {'J8': PLUS_J8},                                                           BPLUS_BOARD,  ),
    0x11:     ('CM',   '1.1', '2014Q2', 'BCM2835', 'Sony',      512,  'eMMC',    1,  0,  False, False, 2,  2,  {'SODIMM': CM_SODIMM},                                                     CM_BOARD,     ),
    0x12:     ('A+',   '1.1', '2014Q4', 'BCM2835', 'Sony',      256,  'MicroSD', 1,  0,  False, False, 1,  1,  {'J8': PLUS_J8},                                                           APLUS_BOARD,  ),
    0x13:     ('B+',   '1.2', '2015Q1', 'BCM2835', 'Egoman',    512,  'MicroSD', 4,  1,  False, False, 1,  1,  {'J8': PLUS_J8},                                                           BPLUS_BOARD,  ),
    0x14:     ('CM',   '1.1', '2014Q2', 'BCM2835', 'Embest',    512,  'eMMC',    1,  0,  False, False, 2,  2,  {'SODIMM': CM_SODIMM},                                                     CM_BOARD,     ),
    0x15:     ('A+',   '1.1', '2014Q4', 'BCM2835', 'Embest',    256,  'MicroSD', 1,  0,  False, False, 1,  1,  {'J8': PLUS_J8},                                                           APLUS_BOARD,  ),
    }

SPI_HARDWARE_PINS = {
    0: {
        'clock':  'GPIO11',
        'mosi':   'GPIO10',
        'miso':   'GPIO9',
        'select': ('GPIO8', 'GPIO7'),
    },
}
