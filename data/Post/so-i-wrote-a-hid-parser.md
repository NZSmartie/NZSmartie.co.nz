---
title: So, I wrote a HID Parser
slug: so-i-wrote-a-hid-parser
summary: There's an amazingly flexible USB specification called HID that most operating systems support
author: nzsmartie
published: 2016-05-14
---

For the past year, I've been working on a game controller for a friend's game.

The idea is pretty simple. There are different kinds of inputs varying from one controller to another. Some are touch, some rely on pressure, the rest are buttons. The aim is to design a device that doesn't require too much setup for the game, work across multiple platforms and be either wired or wireless.

Simple? Not quite.

There's an amazingly flexible USB specification called HID (Human Interface Device), a USB class that most operating systems support without the need for custom drivers. The HID specification is also not exclusive to USB, it may be implemented over Bluetooth, or any hardware interface the OS supports.

However, Reading through the specification the first time was scary.

*Note: I'll be referring to the* ***host*** *as either the application that interacts with the HID device, or the Operating System that supports the device's features.*

HID specifies that devices must provide a **Report Descriptor** a specially formatted binary blob that describes **Input**, **Output** and **Feature** reports, the size of the reports and any grouping of the reports. The only requirement, is that the device describes the application the device falls under *(More on this later)*.
The host is left to interpret and support reports which it understands. For example, operating systems understand a device that describes itself as a mouse with X and Y positional values, along with buttons for left, right or middle mouse clicks.

Because I'm building a game controller that can be customised to report different things. I did some research on how to easily discover what reports a device has and utilise them.

Turns out, this is a very uncommon use for HID, and it's rare for someone to need this ability...

I had thought, since HID has been around for a very long time. (Since the early days of USB), that there'd be a nice way to just know that button 1 was pressed. or that the orientation of the device is upside down. *(Okay... Window's HID Stack will let me know about the button presses, but not a lot about what else >~>)*

A few weeks ago, I set out to write a library in Python 3, to read the report descriptor and return an object that is much more usable in an end user application. The primary goals for this library was to:

  - Serialise or deserialise reports for reading and writing.
  - Allow easy access to reports by simply traversing the object.
  - Literally use a device with no prior knowledge of the device's features or reports.

What I ended up with is [PyHIDParser](https://github.com/NZSmartie/PyHIDParser). Not quite small, but enough for me to continue developing more complex features for the game controller project. It's still in pre-alpha, as I still find myself refactoring the library to make it more suitable for an application developer. Since, I'm testing controller's features in a GUI python app.

I Hope that others may find this library useful. I'm sure that soon enough I'll stabilise the API and mark it as beta  for bug fixes only.
