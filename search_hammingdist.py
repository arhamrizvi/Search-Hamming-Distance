def preprocess(data):
    """
    Reference: Monash Tutor
    """

    arr = [0] * len(data)
    arr[0] = len(data) #put the length of the string in the first position
    left = 0 #alignment
    right = 0 #alignment

    #start from pos 1 till the end of data
    for i in range(1, len(data)):
        #if outside the z-box, then we need to count
        if i > right:
            count = 0
            # while we are still within the string
            # and the letter is the same as the prefix
            # count keeps track of the prefix
            while i + count < len(data) and data[count] == data[i+count]:
                # increment count
                count += 1
            # set the z-value at i
                arr[i] = count
            # if there is a box, update the box boundary
            if count > 0:
                left = i
                right = i + count - 1
        # if inside the box
        else:
            # get the paired prefix index (z-value) to copy
            index_prefix = i - left
            # the remaining length of the box
            remaining = right - i + 1
            #case 2a:
            #if the z-value at prefix is still within the remaining box
            if arr[index_prefix] < remaining:
                # copy the value
                arr[i] = arr[index_prefix]
            # case 2b
            # if the value is the exactly the box
            # then we need to extend/ find a new box
            elif arr[index_prefix] == remaining:
                new_right = right + 1
                while new_right < len(data) and data[new_right] == data[new_right-i]:
                    new_right += 1
                # update the z-array with the extension
                    arr[i] = new_right - i
                # new left and right boundary
                left = i
                right = new_right - 1
            # case 2c
            # if the value is greater than the remaining (going outside the box)
            # then we know only the remaining of the box is the same as the prefix
            # note this is z_array[index_prefix] > remaining
            else:
                arr[i] = remaining
    return arr



def badCharPreprocess(pat):
    #preprocess the pattern and store the last occurrence of every possible character in an array of size = alphabet size

    #create a 2D table which is indexed first by the index of the character c in the alphabet and second by the index i in the pattern
    #This lookup will return the occurrence of c in P with the next-highest index j<i or -1 if there is no such occurrence.
    #array[c] return the left occurrence character.
    #The proposed shift will then be {\displaystyle i-j} i-j, with O(1) lookup time and O(kn) space (a finite alphabet of length k).

    if len(pat) == 0:
        return [[] for a in range(26)]
    table = [[-1] for a in range(26)]
    alpha = [-1 for a in range(26)]
    for i in range(len(pat)):
        char = ord(pat[i].lower())-ord('a')
        alpha[char] = i #converts the pattern character and puts it in alpha
        for j in range(len(alpha)):
            table[j].append(alpha[j])
    return table


#Reference, Book by Dan Gusfield: Algorithms on Strings, Trees and Sequences (1997)
def goodSuffix1(S):
    L = [-1] * len(S)
    N = preprocess(S[::-1])  # S[::-1] reverses S
    N.reverse()
    for j in range(len(S) - 1):
        # Using 𝑁_𝑗, we can define 𝐿′(𝑖) as
        # the largest j so that  𝑁_𝑗 (𝑃) = |𝑡| = 𝑛−𝑖+1.
        i = len(S) - N[j]
        if i != len(S):
            L[i] = j
    return L


def goodSuffix2(S):
    #initialize an array 0 times the length of the pattern
    l = [0]*len(S)
    #pre-process the the pattern
    Z = preprocess(S)
    Z = list(reversed(Z))
    largest = 0
    for i in range(len(Z)):
        #if the values in the Z array = i+1, pick the largest of the value or largest value already stored
        if Z[i] == i+1:
            largest = max(Z[i], largest)
        #start putting the largest element from the back fro the l
        l[len(l)-1-i] = largest
    return l


""""
Reference: http://www-di.inf.puc-rio.br/~laber/StringMatching.pdf
Reference2: https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm#The_Galil_Rule
"""
def boyerMoore(pat, txt):
    #Galils Rule: shift sections that are known to match
    matches = []

    #Preprocessing
    bd = badCharPreprocess(pat)
    L = goodSuffix1(pat)
    l = goodSuffix2(pat)


    current = len(pat) - 1      # alignment of last value of Pattern corresponding to Text
    previous = -1     #alignment of previous phase
    while current < len(txt):
        matched = False
        i = len(pat) - 1  #Patttern
        t = current     #Text
        #start from the end character of pattern
        # while the pattern and text matches, decrease index of pattern and text
        while i >= 0 and t > previous and pat[i] == txt[t]:   # Matches starting from end of P with its corresponding character in T
            i -= 1
            t -= 1
        if i == -1 or t == previous:  #Match
            index = current - len(pat) #the index of the matched item
            matches.append(index + 1) #append match index into the list
            matched = True
            if len(pat)>1:
                current += len(pat) - l[1] #update the current counter by the case
            else:
                current +=1 #increment the current counter
        #else:   # No match, shift by max of bad character and good suffix rules
        if matched != True:
            # for good suffix below
            if i + 1 == len(pat):  # Mismatch happened on first attempt
                goodSuffix = 1
            elif L[i + 1] == -1:  # Matched suffix does not appear anywhere in P
                #the least amount for a prefix of P to match a suffix of t –
                # i.e. using a non-zero value of 𝑙’(𝑖).
                goodSuffix = len(pat) - l[i + 1]
            else:  # Matched suffix appears in P
                #find a copy of 𝑡 which is preceded by a different character –
                # i.e. using a non-zero value of 𝐿’(𝑖).
                goodSuffix = len(pat) - L[i + 1]

            #for bad character below
            char = ord(txt[t].lower()) - ord('a') #convert the text value which has mismatched
            badChar = i - bd[char][i] #subtract the pattern position(i) with the pre-processed value in the specific position

            #choosing between bad character and good suffix
            if badChar >= goodSuffix:
                shift = badChar
            else:
                shift = goodSuffix

           #Galils rule
            if shift>= i+1:
                previous=current
            current += shift
    return matches


def partition(pattern,i):
    length = round(len(pattern) // 2)
    n = len(pattern)
    start = i * length

    # get the minimum of either one so that it doesnt go out of bounds
    # NOTE: the partitions might not be of equal size
    if (i + 1) * length < n:
        end = (i + 1) * length
    else:
        end = n
    return start,end


#text = input()

#pattern = input()

with open('patternfile.txt', 'r') as myfile:
    pattern=myfile.read().replace('\n', '')

with open('textfile.txt', 'r') as myfile:
    text=myfile.read().replace('\n', '')

"""
This is the pigeon hole principle. In order to understand this in depth, i used the following reference
Reference: http://www.cs.jhu.edu/~langmea/resources/lecture_notes/approximate_matching.pdf

The basic idea is to divide the pattern into the number of mismatches allowed +1 so in this case 2 partitions cause only 1 mismatch was alllowed
using the start and end, pass it in the boyermoore algorithm which in an exact matching algorithm
The boyermoore alg. will return the indexes of the matches
The alg. then proceeds to check for the first partition and second partition for matching b/w pattern and text
a counter variable is used to check if the count was more than 1.
If in case it was more than one, it breaks out of the loop, otherwise it continues
the index and count is stored in a dictionary
"""


dicti = {}

for i in range(2):
    start,end = partition(pattern,i)
    matches = boyerMoore(pattern[start:end], text)  # should give a list of where our pattern has matched the text
    #print(matches)
    for m in matches:
        if m < start:  # p is less than the lower bound
            continue  # skip the rest

        if m - start + len(pattern) > len(text):
            continue

        count = 0  # count the number of mismatches between the rest of p and t
        for j in range(start):
            index = m-start+j
            if pattern[j] == text[index]:
                pass
            else:
                count += 1
                if count > 1:
                    break

        for j in range(end, len(pattern)):
            index = m - start + j
            if pattern[j] == text[index]:
                pass
            else:
                count += 1
                if count > 1:
                    break
        if count >1:
            pass
        else:
            dicti[m - start + 1] = count





file = open('output_hammingdist.txt', 'w')
for pos,dist in sorted(dicti.items()):
    file.write(str(pos) + "     "+ str(dist)+"\n")
file.close()