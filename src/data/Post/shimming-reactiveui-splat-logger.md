---
title: Shimming ReactiveUI's Log&lt;T&gt;() To Support ASPNet's ILogger&lt;T&gt;
slug: shimming-reactiveui-logger
summary: 
author: nzsmartie
published: 2017-09-27
---

Picking up Xamarin app development again after some time and decided to tackle the world of Reactive programming that I fell in love with from when I was building Angular2 web apps using reactive extensions.

Having recently developed server side with ASP.Net Core, I got use to using `Ilogger<T>` from `Microsoft.Extensions.Logging.Abstractions`. Was quite handy having a consistant `ILogger` interface everywhere that was immediately compatable with many 3rd party loggers (NLog, Serilog, et al) and even built some libraries of my own that use it that aren't solely intended for ASP.Net. 

Whilst picking up [ReactiveUI](https://reactiveui.net/), they provide their own Service Locator inside of [Splat](https://github.com/reactiveui/splat) and provide their own logging classes that aren't directly compatable with `ILogger<T>` (that I wasn't ready to let go of).

[ReactiveUI's Handbook](https://reactiveui.net/docs/handbook/logging/) instructs developers to add `IEnableLogging` to their classes they wish to log from. And by doing so, they gain access to `this.Log()` thanks the extension method:
```C#
public static IFullLogger Log<T>(this T This) where T : IEnableLogger { /* ... */ }
```

This was done so that your class name (through accessing `T`) would be included in the logger's output to help keep track of where the log was issued. 

Seeing how this was done similarly to `ILogger<T>` which is really just `ILogger`. I wanted to bridge the gap by implementing ASP.Net's ILogger<T> and ReactiveUI's Splat logging. Which first involes implementing ILogger<T> 

```C#
public class ReactiveLogger<TClass> : ILogger<TClass>
{
    public IDisposable BeginScope<TState>(TState state)
    {
        throw new NotImplementedException();
    }

    public bool IsEnabled(LogLevel logLevel)
    {
        throw new NotImplementedException();
    }

    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception exception, Func<TState, Exception, string> formatter)
    {        
        throw new NotImplementedException();   
    }
}
```

Taking a peek into how `Microsoft.Extensions.Logging.Console` processes `public void Log<TState>( ... )` I started out by checking `IsEnabled()`, follwoed by null-checking `formatter` and then creating our error message by the supplied `formatter`, `state` and `extenction` parameters.
```C#
    if (!IsEnabled(logLevel))
        return;
    if(formatter == null)
        throw new ArgumentNullException(nameof(formatter));

    var message = formatter(state, exception);

    if (string.IsNullOrEmpty(message) && exception == null)
        return;
```

You may have noticed a lack of `IEnableLogging` interface on `ReactiveLogger`. That's because the logic behind the `Log<T>()` extension method uses the name of the invoking class. In this case, it'd end up always being `ReactiveLogger`. 

Not very helpful if there's dozens of classes being provided with this logger...

Digging into Splat's `ILogManager` (which gets invoked on behalf of `Log<T>()`) it retreives a memory-cached `IFullLogger` initialised with the name of the invoking class. 

So lets copy this bahaviour

```C#
    // Get Splat's ILogManager
    var factory = (Splat.ILogManager)Splat.Locator.Current.GetService(typeof(Splat.ILogManager))
        ?? throw new Exception($"{nameof(Splat.ILogManager)} was not found. Please ensure your dependency resolver is configured correctly.");

    // Get a logger to reprecent our TClass
    var logger = factory.GetLogger(typeof(TClass));
```

What's `Splat.Locator.Current` you ask? It's ReactiveUI's prefered method of getting services required throughout your application without tightly coupling everyhting. 

> **Note:** You're welcome to replace this, but make sure you're populating services requried by ReactiveUI

We're asking Splat's `ILogManager` to provide us with a `IFullLogger` (in the same way `Log<T>()` does), passing in the the target class's type provided through templating.

All that's left is to invoke the correct logginer method.

```C#
    switch (logLevel)
    {
        case LogLevel.Trace:
            // This is very verbose and can be considered equally annoying as LogLevel.Debug in this case.
        case LogLevel.Debug:
            if (exception != null)
                logger.DebugException($"[{eventId.Id}]: {message}", exception);
            else
                logger.Debug($"[{eventId.Id}]: {message}");
            break;
        case LogLevel.Information:
            if (exception != null)
                logger.InfoException($"[{eventId.Id}]: {message}", exception);
            else
                logger.Info($"[{eventId.Id}]: {message}");
            break;
        case LogLevel.Warning:
            if (exception != null)
                logger.WarnException($"[{eventId.Id}]: {message}", exception);
            else
                logger.Warn($"[{eventId.Id}]: {message}");
            break;
        case LogLevel.Error:
            if (exception != null)
                logger.ErrorException($"[{eventId.Id}]: {message}", exception);
            else
                logger.Error($"[{eventId.Id}]: {message}");
            break;
        case LogLevel.Critical:
            if (exception != null)
                logger.FatalException($"[{eventId.Id}]: {message}", exception);
            else
                logger.Fatal($"[{eventId.Id}]: {message}");
            break;
        case LogLevel.None:
            break;
    }
```

Where We call the appropiate logging methods in `IFullLogger` based on our `logLevel`, if our `exception` is null and the output of the formatted message. 

## The Completed ReactiveLogger
```C#
public class ReactiveLogger<TClass> : ILogger<TClass>
{
    public IDisposable BeginScope<TState>(TState state)
    {
        // Scopes haven't been considered yet and I'll update this article when I need it. 
        throw new NotImplementedException();
    }

    public bool IsEnabled(LogLevel logLevel)
    {
        return true; // Up too you on how you decide to disable logging
    }

    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception exception, Func<TState, Exception, string> formatter)
    {
        if (!IsEnabled(logLevel))
            return;
        if(formatter == null)
            throw new ArgumentNullException(nameof(formatter));

        var message = formatter(state, exception);

        if (string.IsNullOrEmpty(message) && exception == null)
            return;

        // Get Splat's ILogManager
        var factory = (Splat.ILogManager)Splat.Locator.Current.GetService(typeof(Splat.ILogManager))
            ?? throw new Exception($"{nameof(Splat.ILogManager)} was not found. Please ensure your dependency resolver is configured correctly.");

        // Get a logger to reprecent our TClass
        var logger = factory.GetLogger(typeof(TClass));

        switch (logLevel)
        {
            case LogLevel.Trace:
            case LogLevel.Debug:
                if (exception != null)
                    logger.DebugException($"[{eventId.Id}]: {message}", exception);
                else
                    logger.Debug($"[{eventId.Id}]: {message}");
                break;
            case LogLevel.Information:
                if (exception != null)
                    logger.InfoException($"[{eventId.Id}]: {message}", exception);
                else
                    logger.Info($"[{eventId.Id}]: {message}");
                break;
            case LogLevel.Warning:
                if (exception != null)
                    logger.WarnException($"[{eventId.Id}]: {message}", exception);
                else
                    logger.Warn($"[{eventId.Id}]: {message}");
                break;
            case LogLevel.Error:
                if (exception != null)
                    logger.ErrorException($"[{eventId.Id}]: {message}", exception);
                else
                    logger.Error($"[{eventId.Id}]: {message}");
                break;
            case LogLevel.Critical:
                if (exception != null)
                    logger.FatalException($"[{eventId.Id}]: {message}", exception);
                else
                    logger.Fatal($"[{eventId.Id}]: {message}");
                break;
            case LogLevel.None:
                break;
        }
    }
}
```

## Bootstrapping Splat's Service Locator
When it comes to bootstrapping Splat's service locator, it gets a little too verbose as you're forced to register multiple logger types:

```C#
    Locator.CurrentMutable.Register<Microsoft.Extensions.Logging.ILogger<MyService>>(() => new ReactiveLogger<MyService>());
    Locator.CurrentMutable.Register<Microsoft.Extensions.Logging.ILogger<MyotherService>>(() => new ReactiveLogger<MyOtherService>());
    // ...
```

Time to make life a little easier (and reading on your eyes) by using extension methods!

```C#
public static class SplatLocatorExtensions
{
    public static Splat.IMutableDependencyResolver RegisterLogger(this Splat.IMutableDependencyResolver services, Type type)
    {
        // Turn ReactiveLogger<> into ReactiveLogger<type>
        var genericReactiveLogger = typeof(ReactiveLogger<>).MakeGenericType(type);
        // Turn ILogger<> into ILogger<type>
        var genericLogger = typeof(ILogger<>).MakeGenericType(type);

        // Register it!
        services.Register(() => Activator.CreateInstance(genericReactiveLogger), genericLogger);
        return services;
    }

    public static Splat.IMutableDependencyResolver RegisterLogger<TType>(this Splat.IMutableDependencyResolver services)
    {
        // Much simpler as we're dealing with templated types rather than `Type` parameters.
        services.Register(() => new ReactiveLogger<TType>(), typeof(ILogger<TType>));
        return services;
    }
}
```

This allows us to quickly register logging for services that need ILogger<T> like this:
```C#
    Locator.CurrentMutable.RegisterLogger<MyService>()
                          .RegisterLogger<MyOtherService>()
                          // ...
```

This allows for us to easily use ASP.Net's `ILogger<T>` in our Xamarin app when using ReactiveUI as our reactive framework.