# Thermal

Thermal is object oriented Python module for working with POS thermal printers using ESC/POS protocol. Number of different connection types are supported for communicating with printers (Bluetooth and File currently).

Module is designed to be very abstract to allow developers to quickly implement support for printing. After desired connection is configured and printer object is created, all developer needs to do is create `Report` object and add components to it in order of printing.

Once packaged, data can be added, changed and cleared simple print report method is called. Structure of a report never changes while the data does. See example files for more information.

