if __name__ == '__main__':
    def dict_sort(input):
        dict_order = {'a':1,
                      'z':0,
                      'b':2}
        return dict_order.get(input)


    test_dict = {'z':321,
                 'b':222,
                 'a':111,
                 'm':234
                 }

    print(sorted(test_dict,key=dict_sort))
