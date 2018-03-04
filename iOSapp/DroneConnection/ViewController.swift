//
//  ViewController.swift
//  DroneConnection
//
//  Created by Jay on 3/3/18.
//  Copyright © 2018 Jay. All rights reserved.
//

import UIKit
import SwiftSocket

class ViewController: UIViewController {

    @IBOutlet weak var dataLbl: UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        dataLbl.isHidden = true
        let leftSwipe = UISwipeGestureRecognizer(target: self, action: #selector(swipeAction(swipe:)))
        leftSwipe.direction = UISwipeGestureRecognizerDirection.left
        self.view.addGestureRecognizer(leftSwipe)
    }
    
    @IBAction func buttonTap(_: UIButton) {
        let broadcastconnection = UDPClient(address: "255.255.255.255", port: 242*106)
        broadcastconnection.enableBroadcast()
        switch broadcastconnection.send(string: "Hello World"){
        case .success:
            print("Connection successful")
        case .failure(let error):
            print("Errod: \(error)")
        }
        //Global DispatchQueue works on all the threads, asynchronously, in the background without affecting the UI.
        DispatchQueue.global(qos: .background).async {
            let server = UDPServer(address: "0.0.0.0", port: 242*106)
            let (data,remoteip,_)=server.recv(1024)
            print("... receiving data from \(remoteip)")
        //Once all the background threads are completed the program returns to main thread that changes the UI.
            DispatchQueue.main.async {
                if let d=data {
                    let chars: [UInt8] = d
                    //Converting bytes array to string and forcefully unwrapping it.
                    let str = String(bytes: chars, encoding: String.Encoding.utf8)!
                    //Should confirm connection with the router which sends a message with an unique character at the start.
                    //if str.hasPrefix("~"){
                        print("Packet received: \(String(describing: str))")
                        self.dataLbl.isHidden = false
                        self.dataLbl.text = str
                        //server.close()
                       // return
                    //}
                    //else{
                    //    print("Try connecting again.")
                    //}
                }
            }
        }
    }
    
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}

extension UIViewController {
    @objc func swipeAction(swipe:UISwipeGestureRecognizer){
        switch swipe.direction.rawValue {
        case 1:
            performSegue(withIdentifier: "goLeft", sender: self)
        case 2:
            performSegue(withIdentifier: "goRight", sender: self)
        default:
            break
        }
    }
}

