import csv
import sys
import math
import itertools

def main():

    #open file to be read
    with open('trades.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        #open file we will write to
        with open('enrichedTrades.csv', 'w', newline='') as new_csv_file:
            csv_writer = csv.writer(new_csv_file)

            #Set titles for 1st row
            csv_writer.writerow(['LocalTime', 'Symbol', 'EventType', 'Side', 'FillSize', 'FillPrice', 'FillExchange', 'SymbolBought', 'SymbolSold', 'SymbolPosition', 'SymbolNotional', 'ExchangeBought', 'ExchangeSold', 'TotalBought', 'TotalSold', 'TotalBoughtNotional', 'TotalSoldNotional'])
            #skip old 1st row when copying
            next(csv_reader)
            currentLine = 1
            stockBoughtColumn = dict({})
            stockSoldColumn = dict({})
            symbolPositionColumn = dict({})
            symbolNotionalColumn = 0 #no dict required as row calculations will be independant of each other
            exchangeBoughtColumn = dict({}) #track exchanges and there total purchases
            exchangeSoldColumn = dict({})
            totalBoughtColumn = dict({})
            totalSoldColumn = dict({})
            TotalBoughtNotionalColumn = dict({})
            totalSoldNotionalColumn = dict({})

            for line in csv_reader:

                #check line length to check for lunch time then skip line
                if len(line) < 6:
                    csv_writer.writerow(['00:00.0', 'LNCH', 'TIME'])
                    line = next(csv_reader)
                #------------------------------------------

                #Variables ------------
                symbolTracker = line[1]
                sideTracker = line[3]
                fillSizeTracker = int(line[4])
                fillPriceTracker = float(line[5])
                fillExchangeTracker = line[6]

                #----------------------

                line.append(SymbolBought(symbolTracker, sideTracker, fillSizeTracker, stockBoughtColumn))
                line.append(SymbolSold(symbolTracker, sideTracker, fillSizeTracker, stockSoldColumn))
                line.append(SymbolPosition(symbolTracker, sideTracker, fillSizeTracker, symbolPositionColumn))
                line.append(SymbolNotional(fillSizeTracker, fillPriceTracker, symbolNotionalColumn))
                line.append(ExchangeBought(sideTracker, fillSizeTracker, fillExchangeTracker, exchangeBoughtColumn))
                line.append(ExchangeSold(sideTracker, fillSizeTracker, fillExchangeTracker, exchangeSoldColumn))
                line.append(TotalBought(sideTracker, fillSizeTracker, totalBoughtColumn))
                line.append(TotalSold(sideTracker, fillSizeTracker, totalSoldColumn))
                line.append(TotalBoughtNotional(sideTracker, fillSizeTracker, fillPriceTracker, TotalBoughtNotionalColumn))
                line.append(TotalSoldNotional(sideTracker, fillSizeTracker, fillPriceTracker, totalSoldNotionalColumn))


                #write row and inc line count
                csv_writer.writerow(line)
                currentLine += 1

            # Print Standard Output
            # Shares Bought: Total number of shares bought
            sys.stdout.write('Shares Bought: ' + str(totalBoughtColumn.get('b')) + '\n')

            # Shares Sold: Total number of shares sold
            sys.stdout.write('Shares Sold: ' + str(sum(totalSoldColumn.values())) + '\n')

            # Notional Bought: Total value of all shares bought
            sys.stdout.write('Notional Bought: ' + str(TotalBoughtNotionalColumn.get('b')) + '\n')

            # Notional Sold: Total value of all shares sold
            sys.stdout.write('Notional Sold: ' + str(sum(totalSoldNotionalColumn.values())) + '\n')

            # Per Exchange Volumes:
                # For each exchange, the total number of shares bought and sold
                # Sorted by the exchange name
            sys.stdout.write('NASDAQ -> shares bought: ' + str(exchangeBoughtColumn.get('NASDAQ')) + '\n')
            sys.stdout.write('NASDAQ -> shares sold: ' + str(exchangeSoldColumn.get('NASDAQ')) + '\n')
            sys.stdout.write('NYSE -> shares bought: ' + str(exchangeBoughtColumn.get('NYSE')) + '\n')
            sys.stdout.write('NYSE -> shares sold: ' + str(exchangeSoldColumn.get('NYSE')) + '\n')

            # 6.Average Fill Size
            averageFillSize = ((sum(stockBoughtColumn.values()) + sum(stockSoldColumn.values())) / currentLine) 
            sys.stdout.write('Average fill size: ' + str(round(averageFillSize, 2)) + '\n')

            # 7.Median fill size
            #medianFillSize = 0
            #sys.stdout.write('Median fill size: ' + str(MedianFillSize(fillSizeTracker, medianFillSizeTracker)))
            sys.stdout.write('Median fill size: ' + str(MedianFillSize()) + '\n')

            # 8.Top 10 most active stocks. List of stocks with most volume (in total shares traded),
            #in descending order and including the actual volume shares trades in parentheses
            #sys.stdout.write('10 Most Active Symbols: ' + str(ActiveStocks()))
            sys.stdout.write('10 Most Active Symbols: ' + str(ActiveStocks()) + '\n')


#we only track when stocks were bought
def SymbolBought(symbolTracker, sideTracker, fillSizeTracker, stockBoughtColumn):

    #open file to be read
    with open('trades.csv', 'r') as csv_file:

        csv_reader = csv.reader(csv_file)
        next(csv_reader)

        #check if symbolBought already has key (if its already in dict)
        if symbolTracker in stockBoughtColumn:
             #if side was buy we add to the value
            if sideTracker == 'b':
                #if key exists, add to value
                stockBoughtColumn[symbolTracker] += fillSizeTracker
                return stockBoughtColumn.get(symbolTracker)

            #if key exists but its not buy we return zero
            elif sideTracker == 't' or sideTracker == 's':
                return 0

        # else, if stock symbol is not in dict, add key and value
        else:
            if sideTracker == 'b':
                stockBoughtColumn[symbolTracker] = fillSizeTracker
                return stockBoughtColumn.get(symbolTracker)

            #if key doesn't exist, add key and set val to 0 because it wasnt bought
            elif sideTracker == 't' or sideTracker == 's':
                stockBoughtColumn[symbolTracker] = 0
                return stockBoughtColumn.get(symbolTracker)

            #never makes it here can be deleted
            else:
                stockBoughtColumn[symbolTracker] = 0
                return stockBoughtColumn.get(symbolTracker)


def SymbolSold(symbolTracker, sideTracker, fillSizeTracker, stockSoldColumn):
    #open file to be read
    with open('trades.csv', 'r') as csv_file:

        csv_reader = csv.reader(csv_file)
        next(csv_reader)

        #check if symbolBought already has key (if its already in dict)
        if symbolTracker in stockSoldColumn:
             #if side was buy we add to the value
            if sideTracker == 'b':
                #if key exists, return zero as we dont want to add it
                return 0

            #if key exists but its not buy we return zero
            elif sideTracker == 't' or sideTracker == 's':
                stockSoldColumn[symbolTracker] += int(fillSizeTracker)
                return stockSoldColumn.get(symbolTracker)

        # else, if stock symbol is not in dict, add key and value set to zero as we wont track buys
        else:
            if sideTracker == 'b':
                stockSoldColumn[symbolTracker] = 0
                return stockSoldColumn.get(symbolTracker)
                

            #if key doesn't exist, add key and set val add sold amount
            elif sideTracker == 't' or sideTracker == 's':
                stockSoldColumn[symbolTracker] = int(fillSizeTracker)
                return stockSoldColumn.get(symbolTracker)

            #never makes it here can be deleted
            else:
                stockSoldColumn[symbolTracker] = 0
                return stockSoldColumn.get(symbolTracker)

#subtracts bought from sold and returns the difference
def SymbolPosition(symbolTracker, sideTracker, fillSizeTracker, symbolPositionColumn):

    #open file to be read
    with open('trades.csv', 'r') as csv_file:

        csv_reader = csv.reader(csv_file)
        #skip first line
        next(csv_reader)

        #check if symbolBought already has key (if its already in dict)
        if symbolTracker in symbolPositionColumn:
             #if side was buy we add to the value
            if sideTracker == 'b':
                #if key exists, add to value
                symbolPositionColumn[symbolTracker] += fillSizeTracker
                return symbolPositionColumn.get(symbolTracker)

            #if key exists we subtract from value
            elif sideTracker == 't' or sideTracker == 's':
                symbolPositionColumn[symbolTracker] -= fillSizeTracker
                return symbolPositionColumn.get(symbolTracker)

        # else, if stock symbol is not in dict, add key and value
        else:
            if sideTracker == 'b':
                symbolPositionColumn[symbolTracker] = fillSizeTracker
                return symbolPositionColumn.get(symbolTracker)

            #if key doesn't exist, add key and set val to 0 because it wasnt bought
            elif sideTracker == 't' or sideTracker == 's':
                symbolPositionColumn[symbolTracker] = int(-abs(fillSizeTracker))
                return symbolPositionColumn.get(symbolTracker)

            #never makes it here can be deleted
            else:
                symbolPositionColumn[symbolTracker] = 0
                return symbolPositionColumn.get(symbolTracker)

def SymbolNotional(fillSizeTracker, fillPriceTracker, symbolNotionalColumn):
    #open file to be read
    with open('trades.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #skip first line
        next(csv_reader)

        symbolNotionalColumn = fillSizeTracker * fillPriceTracker
        symbolNotionalColumn = round(symbolNotionalColumn, 2)
        return symbolNotionalColumn

def ExchangeBought(sideTracker, fillSizeTracker, fillExchangeTracker, exchangeBoughtColumn):
    #open file to be read
    with open('trades.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #skip first line
        next(csv_reader)

        #check if symbolBought already has key (if its already in dict)
        if fillExchangeTracker in exchangeBoughtColumn:
            #check if purchased and add to sum
            if sideTracker == 'b':
                exchangeBoughtColumn[fillExchangeTracker] += fillSizeTracker
                return exchangeBoughtColumn.get(fillExchangeTracker)

            elif sideTracker == 's' or sideTracker == 't':
                return exchangeBoughtColumn.get(fillExchangeTracker)

        #if the stockExchange key is not yet in the dict
        else:
            if sideTracker == 'b':
                exchangeBoughtColumn[fillExchangeTracker] = fillSizeTracker
                return exchangeBoughtColumn.get(fillExchangeTracker)
            else:
                return 0

def ExchangeSold(sideTracker, fillSizeTracker, fillExchangeTracker, exchangeSoldColumn):
    #open file to be read
    with open('trades.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #skip first line
        next(csv_reader)

        #check if symbolBought already has key (if its already in dict)
        if fillExchangeTracker in exchangeSoldColumn:
            if sideTracker == 'b':
                return exchangeSoldColumn.get(fillExchangeTracker)

            elif sideTracker == 's' or sideTracker == 't':
                exchangeSoldColumn[fillExchangeTracker] += fillSizeTracker
                return exchangeSoldColumn.get(fillExchangeTracker)

        #if the stockExchange key is not yet in the dict
        else:
            if sideTracker == 'b':
                return 0
            else:
                exchangeSoldColumn[fillExchangeTracker] = fillSizeTracker
                return exchangeSoldColumn.get(fillExchangeTracker)
        

def TotalBought(sideTracker, fillSizeTracker, totalBoughtColumn):
    #open file to be read
    with open('trades.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #skip first line
        next(csv_reader)

        #check if symbolBought already has key (if its already in dict)
        if sideTracker in totalBoughtColumn:
            if sideTracker == 'b':
                totalBoughtColumn[sideTracker] += int(fillSizeTracker)
                return totalBoughtColumn.get(sideTracker)

            #elif sideTracker == 's' or sideTracker == 't':
            else:
                totalBoughtColumn[sideTracker] = totalBoughtColumn.get('b')
                return totalBoughtColumn[sideTracker]
        #if the stockExchange key is not yet in the dict
        else:
            if sideTracker == 'b':
                totalBoughtColumn[sideTracker] = int(fillSizeTracker)
                return totalBoughtColumn.get(sideTracker)

            #check dict isnt empty and copy existing val
            elif len(totalBoughtColumn) != 0:
                totalBoughtColumn[sideTracker] = totalBoughtColumn.get('b')
                return totalBoughtColumn[sideTracker]
            else:
                totalBoughtColumn[sideTracker] = totalBoughtColumn.get('b')
                return 0

def TotalSold(sideTracker, fillSizeTracker, totalSoldColumn):
    
    #open file to be read
    with open('trades.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #skip first line
        next(csv_reader)

        #check if symbolBought already has key (if its already in dict)
        if sideTracker in totalSoldColumn:
            if sideTracker == 's' or sideTracker == 't':
                totalSoldColumn[sideTracker] += int(fillSizeTracker)
                #return sum of dict as we track 2 vals
                return sum(totalSoldColumn.values())
            #else since its not empty just return dict total val
            else:
                return sum(totalSoldColumn.values())

        #if the stockExchange key is not yet in the dict
        else:
            if sideTracker == 's' or sideTracker == 't':
                totalSoldColumn[sideTracker] = int(fillSizeTracker)
                return sum(totalSoldColumn.values())
            
            elif len(totalSoldColumn) != 0:
                totalSoldColumn[sideTracker] = sum(totalSoldColumn.values())
                return totalSoldColumn[sideTracker]

            else:
                totalSoldColumn[sideTracker] = int(fillSizeTracker)
                return 0
        


def TotalBoughtNotional(sideTracker, fillSizeTracker, fillPriceTracker, TotalBoughtNotionalColumn):

    #open file
    with open('trades.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #skip first line
        next(csv_reader)

        if sideTracker in TotalBoughtNotionalColumn:
            if sideTracker == 'b':
                TotalBoughtNotionalColumn[sideTracker] += fillSizeTracker * fillPriceTracker
                TotalBoughtNotionalColumn[sideTracker] = round(TotalBoughtNotionalColumn[sideTracker], 2)
                return TotalBoughtNotionalColumn[sideTracker]

            else:
                return round(TotalBoughtNotionalColumn.get('b'), 2)
        
        else:
            if sideTracker == 'b':
                TotalBoughtNotionalColumn[sideTracker] = fillSizeTracker * fillPriceTracker
                TotalBoughtNotionalColumn[sideTracker] = round(TotalBoughtNotionalColumn[sideTracker], 2)
                return TotalBoughtNotionalColumn[sideTracker]

            #check dict isnt empty so we don't print zero when we see a new sideTracker symbol
            elif len(TotalBoughtNotionalColumn) != 0:
                TotalBoughtNotionalColumn[sideTracker] = sum(TotalBoughtNotionalColumn.values())
                TotalBoughtNotionalColumn[sideTracker] = round(TotalBoughtNotionalColumn[sideTracker], 2)
                return TotalBoughtNotionalColumn[sideTracker]

            else:
                TotalBoughtNotionalColumn[sideTracker] = fillSizeTracker
                TotalBoughtNotionalColumn[sideTracker] = round(TotalBoughtNotionalColumn[sideTracker], 2)
                return 0
                

def TotalSoldNotional(sideTracker, fillSizeTracker, fillPriceTracker, totalSoldNotionalColumn):
    #open file
    with open('trades.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #skip first line
        next(csv_reader)

        
        if sideTracker in totalSoldNotionalColumn:
            totalSoldNotionalColumn[sideTracker] += fillSizeTracker * fillPriceTracker
            totalSoldNotionalColumn[sideTracker] = round(totalSoldNotionalColumn[sideTracker], 2)
            return sum(totalSoldNotionalColumn.values())

        else:
            #when adding for the 1st time
            if sideTracker == 's' or sideTracker == 't':
                totalSoldNotionalColumn[sideTracker] = fillSizeTracker * fillPriceTracker
                totalSoldNotionalColumn[sideTracker] = round(totalSoldNotionalColumn[sideTracker], 2)
                return sum(totalSoldNotionalColumn.values())

            else:
                #just return sum of dict
                return round(sum(totalSoldNotionalColumn.values()), 2)

#def MedianFillSize(fillSizeTracker, medianFillSizeTracker):
def MedianFillSize():
    medianNumber = 0
    medianFillSizeTracker = []
    #open file
    with open('trades.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #skip first line
        next(csv_reader)

        # loop to add all values to array for sorting
        for line in csv_reader:
            #check line length to check for lunch time then skip line
            if len(line) < 6:
                line = next(csv_reader)

            fillSizeRow = int(line[4])
            medianFillSizeTracker.append(fillSizeRow)
        
        # Sort numbers into ascending order
        medianFillSizeTracker.sort()

        #check if file length is odd or even
        #if even we half length and get num at that index and get the avg of the two middle numbers
        if len(medianFillSizeTracker) % 2 == 0:
            middleIndex = len(medianFillSizeTracker) / 2
            lowerIndex = int(math.floor(middleIndex))
            higherIndex = int(math.ceil(middleIndex))
            lowerVal = medianFillSizeTracker[lowerIndex]
            higherVal = medianFillSizeTracker[higherIndex]
            medianNumber = (lowerVal + higherVal) / 2
            medianNumber = round(medianNumber)

        else:
            middleIndex = len(medianFillSizeTracker) / 2
            lowerIndex = int(math.ceil(middleIndex))
            medianNumber = medianFillSizeTracker[lowerIndex]

        return medianNumber

def ActiveStocks():

    activeStockTracker = ({})
    #open file
    with open('trades.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        #skip first line
        next(csv_reader)

        # loop to add all values to array for sorting
        for line in csv_reader:
            #check line length to check for lunch time then skip line
            if len(line) < 6:
                line = next(csv_reader)

            symbolTracker = line[1]
            fillSizeRow = int(line[4])

            if symbolTracker in activeStockTracker:
                activeStockTracker[symbolTracker] += int(fillSizeRow)

            else:
                activeStockTracker[symbolTracker] = fillSizeRow

        # Sort dict into descending order
        sortedDict = dict(sorted(activeStockTracker.items(), key=lambda item: item[1], reverse=True))

        # use is slice to get top 10
        descDict = dict(itertools.islice(sortedDict.items(), 10))

        return descDict


#call main function
main()