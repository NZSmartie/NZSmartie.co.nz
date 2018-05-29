---
title: My adventures with CoAP
slug: my-adventures-with-coap
summary: Does anyone see this?
author: nzsmartie
published: 2018-05-30
---

# The Story Behind Wiring CoAP.Net

The Internet of Things fasinates me. Being able to control or monitor physical devices from my mobile phone or connect them with some home automation is fun to think about and cool to show off in practice. Making that a reality is much more of a journey than it needs to be. Where I'm also making that journey incredibly hard on myself mostly because I wanted to do it "right".

There are multiple ways if getting your mobile app to talk to an embedded device (like an Arduino, or ESP8266). The more common ways I kept coming across in the maker community is using HTTP web servers, or MQTT.

Web servers over HTTP as you might guess isn't ideal for embedded systems (well not like it used to be) as HTTP has evolved to keep up with modern internet browsers on fast networks and using powerful CPUs. Having an Arduino talk to a webserver ends up being clunky, requiring a bit too much of it's limited RAM, and a whole bunch of other stuff.

MQTT on the side is actually designed for low power, constrained devices. Providing a simple publish and subscribe messaging protocol. There isn't much to say as MQTT is to the point and it works well for simple setups.

I wasn't particularly impressed with either of the two options available, most notably, they use stateful connections. If a device needs to quickly send out short messages, it must do the whole connection negotiation thing. Not including the TLS handshake. Secondly, MQTT doesn't have much in the way of specifying data formats if it's anything beyond simple values. Making interoperability between platforms or vendors difficult or require prior knowledge.

More research landed me with a fairly new protocol called *Constrained Application Protocol* or *CoAP*. Backed by a IETF proposed standard *RFC 7252*. It's a very light weight protocol that takes the RESTful model from HTTP (including an additional *OBSERVE* verb that lets clients subscribe to a resources). Options (AKA *headers*) are compressed in a easy to parse manner for low memory devices. 

What really sets CoAP apart, is that it's transport agnostic, intended to be used over any unreliable transport. Although the specification does reference UDP as the main transport. If there is any transport that support addressing schemes (Bluetooth LE, Zigbee, 6LowPAN), then CoAP can be used over it. Not only to mention UDP, CoAP supports TCP as well but I have yet to read up on that.

Regarding security, TLS isn't exactly applicable. Amazingly, TLS has a UDP variation called *Datagram Transport Layer Security* or *DTLS*. Which is based on TLS 1.0 and TLS 1.2. Additional parameters are required for using TLS over a stateless connection, such as a cookie (provided by the server). 

## So why did I chose CoAP any way?

CoAP has a lot to offer out of the box which quickly gets you started building IoT solutions. Not tied to any specific vendor or mobile app framework or IoT gateway or cloud infrastructure. Much like HTTP, it's gives applications a familiar RESTful API for accessing everything needed from sensor data, to setting configuration on the device. More importantly, it provides a mechanism for device discovery of any publicly accessible resources in a standardized manner.

Simply put, the device doesn't need to know about your phone, and your phone doesn't need to know about the device (sound familiar?). They will find each other using Multicast that you get with UDP. Very similar to how a Google Chromecast is found by your phone or browser.

The key benefits are

 - Designed for constrained environments (low memory, power, network,etc)
 - Familiar REST API
 - support for many data content formats (application/json, application/xml, etc)
 - Support for resource discovery (through CoRE Link Format `/.well-known/core` *RFC 6970*)
 - works over UDP or TCP
 - A Security layer is support though DTLS (based on TLS)

## Working with CoAP

I started to write my own IoT minimal framework with a few key points in mind

  - Something that was easy to set up and start using. (Think Zero-Config)
  - Provides examples of Clean UI/UX for the consumer to use.
  - Plenty of examples of different scenarios of the framework. 
    - Garage Door
    - Temperature control
  - Works on cheap and easy to get hardware
    - ESP8266 (with limitations), ESP32, Arduino, etc...

Quickly, I encountered a minor issue of a serious lack of tools for developemnt and testing that just worked... 

For example, There is a (now unusable) Firefox plugin, *Copper (Cu)*, which was was a simple to the point REST client with a range of settings for tweaking messages. It worked, but wasn't very practical for development. And now you need to run an out of date portable Firefox to use it. 

LibCoAP provide a cli, `coap-client`, but that's mostly useful for scripting or cli based testing.

So I set out to build my own tool. How hard can it be?

## My First Misadventure

IETF RFCs often have associated IANA registries, that is, a living part of the RFC allowing future extensions to the RFC. CoAP has an IETF registry for content formats, resource types and interface types.

That is where I had discovered *Open Inter-Connect* (OIC), an Iot specification produced by the OpenConnectivity Foundation (OCF). An alliance of multiple companies with the desire to make consumer IoT devices interoperable with each other out of the box.

Sweet!

First impressions of OIC showed extensive coverage of discovery, providing a large set of primitives for most physical devices, and several other well though out aspects. It covers Security, grouping devices and device management.

First step was to decide on the framework used for developing this magical tool. .Net is my strong point and naturally, decided Xamarin.Forms would be a good way to build a cross platform application.

I needed a CoAP library, to build a OIC library... Which is where things fell short. There existed a coupld of CoAP libraries, targeting .Net Framework and assumed a UDP connection. And at the time, didn't support .Net Standard (more on that later). So i set out to write my own CoAP library. 

This is around the time .Net Portable was still a thing and Xamarin just started to support .Net Standard. I'm so glad .Net Portable is behind us now.

I faced a couple of challenges when building my own CoAP library, learning about .Net Standard, building a reliable network stack for CoAP. Considering what the API would look like. Setting up tests. Testing thouroughly. Learning that my tests still aren't enough. 

Did you know that `List<T>.Sort()` and `IEunumerable<T>.OrderBy()` give different results...?

Developing a OIC library also had a lot more challenges of it's own. Forking JSON.Net to support CBOR (effectively binary json with tags), code generation of the primitives, and more importantly, a lack of physical devices to play with. 

My first Cross platform app, OICExplorer, turned into a sad story. Xamarin.Forms had a lot of brick walled issues. Trying to develop a nice User Experience, while following the native platform's User Interface guidelines (ie. Material Design, UWP, iOS) was a nightmare. I hear that MS Build announced future plans to imporive on this. for at the time, this wasn't feasible.

Trying to design a Xamarin.Forms app quickly became impractical due to it's lack of design flexibility. That paired with bizzar quirks of OIC itself, a specification that was designed to only work with existing products prodiced by members of the OCF alliance. Not actually intended for everyday household items. These factors became frustrating and lead me to rethink my requirements and start again.

#### More to Follow. Stay Tuned