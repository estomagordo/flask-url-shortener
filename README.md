A sample URL shortener using Python Flask.

To install and run, make sure you have Python 3 installed.
You will also need Flask (pip install requirements.txt).
Then just run the program from a console of your liking (python main.py).

This starts the service in debug mode on localhost:5000.
A more production-like setup is beyond this scope.

To run the unit test suite, just run pytest from within the project folder.

A few notes on assumptions and decisions made:

A URL is considered valid if it "looks like" a URL.
This gets determined through parsing with a regular expression.
This is notoriously hard (impossible?) to get right, so this program is only
approximately right in that regard.
The alternative would be to try and actually connect to the URL, perhaps with a HEAD request.
That approach has a couple of drawbacks, though.
For one, it is more time consuming. And secondly, it would reject resources that are
temporarily unavailable.

URL shortening happens with hashing and subsequent conversion to base 64.
The Blake2b algorithm was chosen for its relative speed, and ease to configure an output size.
For more performance critical scenarios, a different algorithm, such as md5 may be explored.
The takeaway here is that cryptographical security is not very important.
What's important is collision detection, and this project achieves this through randomization
of the input value until a previously unseen hash is generated.

The service utilizes an in-memory dictionary to represent all the shortened URLs.
In a real-life, large-scale scenario, something fancier would be needed. This would also
have implications for how we determine whether a hash is unique or not.

Storage-wise, it is likely that all shortened URLs would fit in main memory on one machine.
Back of the envelope calculation:
URLs may typically be quite long, with lots of parameters. Let's say 200 bytes on average.
Add to that roughly 50 bytes (the key, that is the shortened URL, makes up a little of that,
but we might want to add auxiliary data, such as a time stamp and a sender).
So roughly 4 entries fit in a kilobyte, or 4,000,000 in a gigabyte.
This suggests a powerful machine could store in the neighbourhood of 100 million entries.

This is good news, as URLs can be kept in memory, for fast lookups. Using Redis or Memcached.
But we also need persistent storage to prevent data loss, and also some sort of load balancing
to handle large amounts of traffic.
From the standpoint of this application, it would have to write data to a remote endpoint that
abstracts away these concerns for our web application. That endpoint will be responsible for
distributing the newly written key in its cluster, and then, as a separate process, writing
it to persistent storage. This persistent storage would act as the main source of truth,
and also house any data that does not fit in RAM of the read endpoints, should our service
grow beyond our initial visions. This would also mean that we would move the caching logic
to the write cluster.