---
title: async, EventHandler and Exceptions
slug: async-eventhandler-exceptions
summary: Dealing with exceptions thrown by async event handlers
author: nzsmartie
published: 2017-08-18
---

Hopefully this will 

  - Help lost developers who dealt with a similar situation to myself
  - Get feedback if this is a good approach to dealing with throwing exceptions in an `async` `EventHandler`

**Throwing Exceptions From Events**

A developer would typically add an event to their class

```C#
public class MyClass
{
    public event EventHandler OnSomeEvent;
    
    public void TriggerSomeEvent()
    {
        try
        {
            OnSomeEvent?.Invoke(this, new EventArgs());
        }
        catch(Exception ex)
        {
            // Handle exception things here
        }
    }
}
```

A subscriber class may listen to the event using 

    thatClass.OnSomeEvent += (sender, args) => Console.WriteLine("Some event happened");

If the subscriber was to throw an exception, or it failed to handle an exception on it's own. It would be passed back to `TriggerSomeEvent` 

**Throwing Exceptions From `async` Events**

This is where things get tricky. When a listener class subscribes with an async delegate, and throws an exception. it does no get handled by `TriggerSomeEvent`

```C#
thatClass.OnSomeEvent += async (sender, args) => 
{
    await Task.Yield();
    throw new Exception();
}
```

`TriggerSomeEvent` will never catch the event for a couple of reasons. The first being that the above delegate is `async void`, there's no `Task` to store the exception into, and that the delegate is not awaited. 

After exploring my my options, I considered using an `AsyncEventHandler`

```C#
public delegate Task AsyncEventHandler(object sender, EventArgs e);
// and
public delegate Task AsyncEventHandler<TEventArgs>(object sender, TEventArgs e);
```

Compared to C#'s EventHander 

```C#
public delegate void EventHandler(object sender, EventArgs e);
// and
public delegate void EventHandler<TEventArgs>(object sender, TEventArgs e);
```

The only difference being that AsyncEventHandler returns type `Task` instead of `void`

Invoking an `AsyncEventHandler` is slightly more complicated

```C#
public delegate Task AsyncEventHandler(object sender, EventArgs e);

public class MyEventClass
{
    /// <summary>
    /// A async event delegate
    /// </summary>
    public AsyncEventHandler MyAsyncEvent;

    /// <summary>
    /// A typical event delegate
    /// </summary>
    public EventHandler MyEvent;

    /// <summary>
    /// Invokes all listeners and awaits any that are async
    /// </summary>
    /// <returns></returns>
    public async Task TriggerAsyncEvent()
    {
        try
        {
            await Task.WhenAll(GetAwaitableAsyncEvents()).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            // Exceptions are caught here
        }
    }

    /// <summary>
    /// Invoked from <see cref="TriggerAsyncEvent"/> to return async delegates to await
    /// </summary>
    /// <returns></returns>
    private IEnumerable<Task> GetAwaitableAsyncEvents()
    {
        foreach (var listener in MyAsyncEvent.GetInvocationList())
            if (listener.DynamicInvoke(this, new EventArgs()) is Task task)
                yield return task;
    }

    /// <summary>
    /// Typical event invokation 
    /// </summary>
    public void TriggerEvent()
    {
        try
        {
            MyEvent(this, new EventArgs());
        }
        catch (Exception ex)
        {
            // Exceptions are caught here
        }
    }
}
```

In both cases, calling `TriggerEventAsync()` or  `TriggerEvent()` will handle exceptions thrown in either synchronous or asynchronous code blocks.

I have written some tests with Nunit3 and .Net Core 1.1 to illustrate working examples of exceptions being correctly handled up the stack. 

[Handle Exceptions from async EventHandler with Nunit tests ](https://gist.github.com/NZSmartie/2b66924cffc98047f995c7f3813046eb)

Feedback is appreciated!