#!/usr/bin/python
# -*- coding: utf-8 -*-
from body import BoenBot
import urllib3


if __name__ == '__main__':
	urllib3.disable_warnings()
	boenBot = BoenBot()
	boenBot.mainloop()