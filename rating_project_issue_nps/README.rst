.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==========================================
 Project issue rating: Net Promoter Score
==========================================

This module implements the `Net Promoter Score`_ (NPS) customer
satisfaction measure.

.. _`Net Promoter Score`: http://www.netpromotersystem.com

The main user visible differences with the standard `rating` module
are:

- the evaluation question reads: "How likely is it you recommend us to
  a friend?"

- the evaluation range is:

  * from 0 to 6: evaluators are considered as detractors
  * 7 and 8: evaluators are considered passives
  * 9 and 10: evaluators are considered promoters

  For more information, see the `Net Promoter Score`_ description page.

From the company point of view, the global indicator (the NPS) is
computed as follows::

  promoters% - detractors%

This indicators is the one displayed on the project board. It may
optionally be publicly displayed on your website or integrated
anywhere using an iframe. It is computed for the last 30 days of
activity.
