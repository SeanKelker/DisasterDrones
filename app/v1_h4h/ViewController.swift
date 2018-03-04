//
//  ViewController.swift
//  v1_h4h
//
//  Created by Steven Bucher on 3/3/18.
//  Copyright © 2018 Steven Bucher. All rights reserved.
//

import UIKit
//import SwiftSocket

class ViewController: UIViewController, UITableViewDelegate, UITableViewDataSource {
    
    @IBOutlet weak var recieveBtn: UIButton!
    @IBOutlet weak var sendBtn: UIButton!
    
    let connection = true
    let data = ["Nearest City: Seattle", "Authorties Coming"]
    @IBOutlet weak var conStatus: UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        conStatus.isHidden = true
        if !connection {
            conStatus.isHidden = false
        }
        recieveBtn.layer.cornerRadius = 10
        recieveBtn.clipsToBounds = true
        sendBtn.layer.cornerRadius = 10
        sendBtn.clipsToBounds = true
        //recieveBtn.isHidden = true
        sendBtn.isHidden = true
        
        let leftSwipe = UISwipeGestureRecognizer(target: self, action: #selector(swipeAction(swipe:)))
        leftSwipe.direction = UISwipeGestureRecognizerDirection.left
        self.view.addGestureRecognizer(leftSwipe)
        
    }

    @IBAction func recieveData(_ sender: Any) {
        
        print("RECIEVE DATA")
    }
    
    
    func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return data.count
    }
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        
        
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
        cell.textLabel?.textColor = UIColor.white
        cell.textLabel?.text = data[indexPath.row]
        
        return cell
    }
}

extension UIViewController{
    @objc func swipeAction(swipe:UISwipeGestureRecognizer){
        switch swipe.direction.rawValue {
        case 3:
            performSegue(withIdentifier: "goLeft", sender: self)
        case 2:
           performSegue(withIdentifier: "goRight", sender: self)
        default:
            //performSegue(withIdentifier: "goRight", sender: self)
            break
        }
    }
}





