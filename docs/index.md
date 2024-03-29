---
layout: default
---

![Brain Tree](assets/images/brain-tree.jpg)

We are a cyber security startup in steath mode. We have decided to release this proof of concept to the public on GitHub.

# The problem

* When recruiting you need to accept resumes from anyone.

* Resumes are usually word documents which might contain macro viruses or other threats.

* Our competitors could use a virus in a resume to infect our computers and exfiltrate information about who we are, who has applied to join us, and our secret IP.

* Our internal recruiter is non technical, part time, and not equipped to deal with such cyber threats.

# The solution.

* Scan resumes on upload, an only deliver to the recruiter if they are clean.

* We use the [SophosLabs Intelix](https://api.labs.sophos.com/doc/index.html) public scanning API to scan all uploaded files.

* There is basic plumbing in AWS with buckets, lambdas, queues, topics etc to make it all work.

* After each upload and scan, a link to the Resume is sent to our recruiter with information on the scan result.

# Proof of concept website.

As a demo, the resume upload page is available for you to try out via a [static S3 website](https://ostriches-web.s3.eu-central-1.amazonaws.com/index2.html).

Interested in working in cyber security? Contact us at [Unbiased.Ostriches@gmail.com](mailto:Unbiased.Ostriches@gmail.com)
