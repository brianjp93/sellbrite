# sellbrite
- A completely hackish way of editing sellbrite skus using selenium
- Can accomplish basic tasks like
  - retrieve stock, upc, bin location, title given a sku
  - update stock
  - update bin location
- The lack of an api makes batch updates difficult but not impossible, perhaps I will add more to this code.  We'll try not to spam sellbrite's servers too much though.

### Dependencies
- python 2.7 (Untested in other versions.)
- selenium
- chromedriver https://sites.google.com/a/chromium.org/chromedriver/downloads
- beautifulsoup4

### Setup
- rename ```your.data``` to ```sb.data```
  - fill in the ??? with the appropriate data.

### Usage

#### Get Basic Data
- Assuming we have a sku 1234
```python
from sellbrite import Sellbrite
sb = Sellbrite()
info = sb.getDetailedInfo("1234")
```
- Here, info is a dictionary that looks like:
```python
{"title": title, "bin": bin_loc, "quantity": quantity, "upc": upc}
```

#### Update Quantity
```python
sb.updateQuantity("1234", "10")  # update sku 1234 with quantity 10
```

#### Update Bin Location
```python
sb.updateBinLocation("1234", "A100")  # update sku 1234 with location A100
```


### License
https://opensource.org/licenses/MIT