# Project XX Signaling System Design Specification

**Document No.**: DOC-002
**Version**: v1.5
**Project**: XX Urban Rail Transit Line 2

---

## Page 1: Design Basis

This design is based on the following standards:
- Code for Design of Urban Rail Transit Signaling System (CJJ/T 248-2018)
- Rail Transit Signaling Safety-Related Systems (GB/T 28809)
- Project Technical Specification v3.2

> page=1

## Page 3: Signaling System Scheme

The signaling system design for this project is based on CBTC technology, implementing moving block control. The system architecture is divided into three layers:

1. **Central Layer**: ATS subsystem, achieving line-level train operation monitoring and dispatch management.
2. **Wayside Layer**: Computer interlocking system, track circuits, and balises, achieving route control and train positioning.
3. **Onboard Layer**: ATP/ATO onboard equipment, achieving train protection and automatic driving.

Train-to-ground communication uses 2.4GHz spread spectrum communication with a transmission rate of no less than 2Mbps. Trains can maintain safe stopping after communication interruption.

Under moving block mode, the minimum train headway can reach 90 seconds, increasing line capacity by approximately 15-20% compared to traditional fixed block systems.

> page=3
