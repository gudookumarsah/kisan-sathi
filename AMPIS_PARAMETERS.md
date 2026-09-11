# AMPIS parameter reference

Everything here was confirmed working against `https://ampis.gov.np/market-price-comparison`
as a plain GET request — no login, no session, no AJAX needed.

## URL pattern
```
https://ampis.gov.np/market-price-comparison
  ?uid_entityreference_filter={MARKET_ID}
  &field_market_rate_year_target_id_entityreference_filter={YEAR_ID}
  &field_commodity_category_target_id_entityreference_filter={CATEGORY_ID}
  &field_market_rate_month_target_id={MONTH_ID}
  &field_market_rate_commodity_target_id_entityreference_filter={COMMODITY_ID}
  &field_market_rate_day_target_id={DAY}
```

## Markets (all 12 AMPIS markets — we track 6)
| Market | ID |
|---|---|
| धरान, सुनसरी | 6 |
| बिर्तामोड, झापा | 5 |
| **ढल्केवर, धनुषा** ✅ tracked | **7** |
| कमलामाई, सिन्धुली | 8 |
| कावासोती, नवलपुर | 9 |
| **पोखरा, कास्की** ✅ tracked | **10** |
| **बुटवल, रुपन्देही** ✅ tracked | **11** |
| **कोहलपुर, बाँके** ✅ tracked | **12** |
| बिरेन्द्रनगर, सुर्खेत | 13 |
| अत्तरिया, कैलाली | 14 |
| **लालबन्दी, सर्लाही** ✅ tracked | **15** |
| **कालीमाटी, काठमाडौं** ✅ tracked | **23** |

## Category
तरकारी (vegetable) = `2` — confirmed working for all six tracked crops,
including आलु (potato) which is technically a "tuber" category elsewhere on
the site. If a future crop swap returns no data under category 2, try `All`.

## Commodities (the six we track)
| Crop | AMPIS name | ID |
|---|---|---|
| tomato | गोलभेंडा ठुलो (नेपाली) | 409 |
| potato | आलु रातो (मुढे) | 378 |
| onion | प्याज सुकेको (नेपाली) | 1694656 |
| cauli | काउली (तराई) | 398 |
| cabbage | बन्दा (तराई) | 401 |
| chili | खुर्सानी हरियो (लाम्चो) | 1694671 |

To add a crop: open ampis.gov.np, pick it from the "कृषि उपज" dropdown in
dev tools, and read the `value` off the selected `<option>`.

## Years (NOT predictable — must be manually found each BS year)
| BS Year | ID |
|---|---|
| 2080 | 16 |
| 2081 | 446538 |
| 2082 | 894719 |
| 2083 | 1614822 |

When BS year 2084 begins (~mid-April 2027), `scraper.py` will start logging
a warning and skipping runs until this table is updated. Find the new ID the
same way: open the site, pick the new year, check the URL/request.

## Months (fixed, stable — these won't change)
| BS Month | Name | ID |
|---|---|---|
| 1 | बैशाख | 33 |
| 2 | जेठ | 34 |
| 3 | असार | 35 |
| 4 | साउन | 36 |
| 5 | भदौ | 37 |
| 6 | असोज | 38 |
| 7 | कार्तिक | 39 |
| 8 | मंसिर | 40 |
| 9 | पुष | 41 |
| 10 | माघ | 42 |
| 11 | फागुन | 43 |
| 12 | चैत | 44 |

## Day
Plain integer, 1–32. No lookup needed.
